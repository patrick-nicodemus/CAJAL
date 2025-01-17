"""
Functions for computing the quantized Gromov-Wasserstein distance and the SLB between
metric measure spaces, and related utilities for file IO and parallel computation.
"""
# std lib dependencies
import sys
import itertools as it
import csv
from typing import Iterable, Iterator, Collection, Optional, Literal
from math import sqrt

if "ipykernel" in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

# external dependencies
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import squareform, pdist
from scipy import sparse
from scipy import cluster

from multiprocessing import Pool

from .slb import l2
from .gw_cython import quantized_gw_cython, qgw_init_cost

from .run_gw import (_batched, cell_iterator_csv,
                     Distribution, DistanceMatrix,
                     Matrix, uniform, Array,
                     MetricMeasureSpace
                     )


def distance_inverse_cdf(
    dist_mat: npt.NDArray[np.float_], measure: npt.NDArray[np.float_]
):
    """
    Compute the cumulative inverse distance function between two cells.

    :param dX: Vectorform (one-dimensional) distance matrix for a space, of
    length N * (N-1)/2, where N is the number of points in dX.
    :param measure: Probability distribution on points of X, array of length N,
    entries are nonnegative and sum to one.

    :return: The inverse cumulative distribution function of the space, what
    Memoli calls "f_X^{-1}"; intuitively, a real valued function on the unit
    interval such that f_X^{-1}(u) is the distance `d` in X such that u is the
    proportion of pairs points in X that are at least as close together as `d`.
    """
    index_X = np.argsort(dist_mat)
    dX = np.sort(dist_mat)
    mX_otimes_mX_sq = np.matmul(measure[:, np.newaxis], measure[np.newaxis, :])
    mX_otimes_mX = squareform(mX_otimes_mX_sq, force="tovector", checks=False)[index_X]

    f = np.insert(dX, 0, 0.0)
    u = np.insert(mX_otimes_mX, 0, measure @ measure)

    return (f, u)


def slb_distribution(
    dX: Array,
    mX: Distribution,
    dY: Array,
    mY: Distribution,
):
    """
    Compute the SLB distance between two cells equipped with a choice of distribution.

    :param dX: Vectorform distance matrix for a space X, of length N * (N-1)/2,
        (where N is the number of points in X)
    :param mX: Probability distribution vector on X.
    :param dY: Vectorform distance matrix, of length M * (M-1)/2
        (where M is the number of points in X)
    :param mY: Probability distribution vector on X.
    """
    f, u = distance_inverse_cdf(dX, mX)
    g, v = distance_inverse_cdf(dY, mY)
    cum_u = np.cumsum(u)
    cum_v = np.cumsum(v)
    return 0.5 * sqrt(l2(f, u, cum_u, g, v, cum_v))


# SLB
def _init_slb_pool(sorted_cells, distributions):
    """
    Initialize the parallel SLB computation.

    Declares a global variable accessible from all processes.
    """
    global _SORTED_CELLS
    _SORTED_CELLS = list(zip(sorted_cells, distributions))


def _global_slb_pool(p: tuple[int, int]):
    """Compute the SLB distance between cells p[0] and p[1] in the global cell list."""
    i, j = p
    dX, mX = _SORTED_CELLS[i]
    dY, mY = _SORTED_CELLS[j]
    return (i, j, slb_distribution(dX, mX, dY, mY))
    # return (i, j, slb_cython(_SORTED_CELLS[i], _SORTED_CELLS[j]))


def slb_parallel_memory(
    cell_dms: list[DistanceMatrix],
    cell_distributions : Optional[Iterable[Distribution]],
    num_processes: int,
    chunksize: int = 20,
) -> DistanceMatrix:
    """
    Compute the SLB distance in parallel between all cells in `cell_dms`.

    :param cell_dms: A collection of distance matrices. Probability distributions
        other than uniform are currently unsupported.
    :param num_processes: How many Python processes to run in parallel
    :param chunksize: How many SLB distances each Python process computes at a time

    :return: a square matrix giving pairwise SLB distances between points.
    """
    if cell_distributions is None:
        cell_distributions = [uniform(cell_dm.shape[0]) for cell_dm in cell_dms]
    cell_dms_sorted = [np.sort(squareform(cell, force="tovector")) for cell in cell_dms]
    N = len(cell_dms_sorted)

    with Pool(
        initializer=_init_slb_pool,
        initargs=(cell_dms_sorted, cell_distributions),
        processes=num_processes,
    ) as pool:
        slb_dists = pool.imap_unordered(
            _global_slb_pool, it.combinations(iter(range(N)), 2), chunksize=chunksize
        )
        arr = np.zeros((N, N))
        for i, j, x in slb_dists:
            arr[i, j] = x
            arr[j, i] = x

    return arr


def slb_parallel(
    intracell_csv_loc: str,
    num_processes: int,
    out_csv: str,
    chunksize: int = 20,
) -> None:
    """
    Compute the SLB distance in parallel between all cells in the csv file `intracell_csv_loc`.

    The files are expected to be formatted according to the format in
    :func:`cajal.run_gw.icdm_csv_validate`. Probability distributions
    other than uniform are currently unsupported,

    :param cell_dms: A collection of distance matrices
    :param num_processes: How many Python processes to run in parallel
    :param chunksize: How many SLB distances each Python process computes at a time
    """
    names, cell_dms = zip(*cell_iterator_csv(intracell_csv_loc))
    slb_dmat = slb_parallel_memory(cell_dms, None, num_processes, chunksize)
    NN = len(names)
    total_num_pairs = int((NN * (NN - 1)) / 2)
    ij = tqdm(it.combinations(range(NN), 2), total=total_num_pairs)
    with open(out_csv, "w", newline="") as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["first_object", "second_object", "slb_dist"])
        batches = _batched(
            ((names[i], names[j], str(slb_dmat[i, j])) for i, j in ij), 2000
        )
        for batch in batches:
            csv_writer.writerows(batch)


class quantized_icdm:
    """
    A "quantized" intracell distance matrix.

    A metric measure space which has been equipped with a given clustering; it
    contains additional data which allows for the rapid computation of pairwise
    GW distances across many cells. Users should only need to understand how to
    use the constructor. Usage of this class will result in high memory usage if
    the number of cells to be constructed is large.

    :param cell_dm: An intracell distance matrix in squareform.
    :param p: A probability distribution on the points of the metric space
    :param num_clusters: How many clusters to subdivide the cell into; the more
        clusters, the more accuracy, but the longer the computation.
    :param clusters: Labels for a clustering of the points in the cell. If no clustering
        is supplied, one will be derived by hierarchical clustering until
        `num_clusters` clusters are formed. If a clustering is supplied, then
        `num_clusters` is ignored.
    """

    n: int
    # 2 dimensional square matrix of side length n.
    icdm: npt.NDArray[np.float64]
    # "distribution" is a dimensional vector of length n,
    # a probability distribution on points of the space
    distribution: npt.NDArray[np.float64]
    # The number of clusters in the quantized cell, which is *NOT* guaranteed
    # to be equal to the value of "clusters" specified in the constructor. Check this
    # field when iterating over clusters rather than assuming it has the number of clusters
    # given by the argument `clusters` to the constructor.
    ns: int
    # A square sub-matrix of icdm, the distance matrix between sampled points. Of side length ns.
    sub_icdm: npt.NDArray[np.float64]
    # q_indices is a 1-dimensional array of integers of length ns+1. For i,j < ns,
    # icdm[sample_indices[i],sample_indices[j]]==sub_icdm[i,j].
    # sample_indices[ns]==n.
    q_indices: npt.NDArray[np.int_]
    # The quantized distribution; a 1-dimensional array of length ns.
    q_distribution: npt.NDArray[np.float64]
    c_A: float
    c_As: float
    A_s_a_s: npt.NDArray[np.float64]
    # This field is equal to np.dot(np.dot(np.multiply(icdm,icdm),distribution),distribution)

    def _sort_icdm_and_distribution(
        cell_dm: DistanceMatrix,
        p: Distribution,
        clusters: npt.NDArray[np.int_],
    ) -> tuple[DistanceMatrix, Distribution, npt.NDArray[np.int_]]:
        """
        Sort the cell distance matrix so that points in the same cluster are grouped
        together and the points of each cell are in descending order.

        :param clusters: A vector of integer cluster labels telling which
            cluster each point belongs to, cluster labels are assumed to be contiguous and
            start at 1.

        :return: A sorted cell distance matrix, distribution, and a vector of
            integers marking the initial starting points of each cluster. (This
            has one more element than the number of distinct clusters, the last
            element is the length of the cell.)
        """

        indices: npt.NDArray[np.int_] = np.argsort(clusters)
        cell_dm = cell_dm[indices, :][:, indices]
        p = p[indices]

        for i in range(1, len(set(clusters)) + 1):
            permutation = np.nonzero(clusters == i)[0]
            this_cluster = cell_dm[permutation, :][:, permutation]
            medoid = np.argmin(sum(this_cluster))
            new_local_indices = np.argsort(this_cluster[medoid])
            cell_dm[permutation, :] = cell_dm[permutation[new_local_indices], :]
            cell_dm[:, permutation] = cell_dm[:, permutation[new_local_indices]]
            indices[permutation] = indices[permutation[new_local_indices]]
            p[permutation] = p[permutation[new_local_indices]]
            # q.append(np.sum(p[permutation]))

        q_indices = np.asarray(
            np.nonzero(np.r_[1, np.diff(np.sort(clusters)), 1])[0], order="C"
        )

        return (np.asarray(cell_dm, order="C"), p, q_indices)

    def __init__(
        self,
        cell_dm: DistanceMatrix,
        p: Distribution,
        num_clusters: Optional[int],
        clusters: Optional[npt.NDArray[np.int_]] = None,
    ):
        # Validate the data.
        assert len(cell_dm.shape) == 2

        self.n = cell_dm.shape[0]

        if clusters is None:
            # Cluster the data and set icdm, distribution, and ns.
            Z = cluster.hierarchy.linkage(squareform(cell_dm), method="centroid")
            clusters = cluster.hierarchy.fcluster(
                Z, num_clusters, criterion="maxclust", depth=0
            )

        icdm, distribution, q_indices = quantized_icdm._sort_icdm_and_distribution(
            cell_dm, p, clusters
        )

        self.icdm = icdm
        self.distribution = distribution
        self.ns = len(set(clusters))
        self.q_indices = q_indices

        clusters_sort = np.sort(clusters)
        self.icdm = np.asarray(cell_dm, order="C")
        self.distribution = p

        # Compute the quantized distribution.
        q = []
        for i in range(self.ns):
            q.append(np.sum(distribution[q_indices[i] : q_indices[i + 1]]))
        q_arr = np.array(q, dtype=np.float64, order="C")
        self.q_distribution = q_arr
        assert abs(np.sum(q_arr) - 1.0) < 1e-7
        medoids = np.nonzero(np.r_[1, np.diff(clusters_sort)])[0]

        A_s = cell_dm[medoids, :][:, medoids]
        # assert np.all(np.equal(original_cell_dm[:, indices][indices, :], cell_dm))
        self.sub_icdm = np.asarray(A_s, order="C")
        self.c_A = np.dot(np.dot(np.multiply(cell_dm, cell_dm), p), p)
        self.c_As = np.dot(np.multiply(A_s, A_s), q_arr) @ q_arr
        self.A_s_a_s = np.dot(A_s, q_arr)

    @staticmethod
    def of_tuple(p):
        cell_dm, p, num_clusters, clusters=p
        return quantized_icdm(cell_dm,p, num_clusters,clusters)

    def of_ptcloud(
        X: Matrix,
        distribution: Distribution,
        num_clusters: int,
        method: Literal["kmeans"] | Literal["hierarchical"] = "kmeans",
    ):
        dmat = squareform(pdist(X), force="tomatrix")
        if method == "hierarchical":
            return quantized_icdm(dmat, distribution, num_clusters)
        # Otherwise use kmeans.
        # TODO: This will probably give way shorter than the amount of cells.
        _, clusters = cluster.vq.kmeans2(
            X,
            num_clusters,
            minit='++'
        )
        return quantized_icdm(dmat, distribution, None, clusters)


def quantized_gw(
    A: quantized_icdm,
    B: quantized_icdm,
    initial_plan: Optional[npt.NDArray[np.float_]] = None,
) -> tuple[sparse.csr_matrix, float]:
    """
    Compute the quantized Gromov-Wasserstein distance
    between two quantized metric measure spaces.

    :param initial_plan: An initial guess at a transport
    plan from A.sub_icdm to B.sub_icdm.
    """

    if initial_plan is None:
        T_rows, T_cols, T_data = quantized_gw_cython(
            A.distribution,
            A.sub_icdm,
            A.q_indices,
            A.q_distribution,
            A.A_s_a_s,
            A.c_As,
            B.distribution,
            B.sub_icdm,
            B.q_indices,
            B.q_distribution,
            B.A_s_a_s,
            B.c_As,
        )
    else:
        init_cost = -2 * (A.sub_icdm @ initial_plan @ B.sub_icdm)
        T_rows, T_cols, T_data = qgw_init_cost(
            A.distribution,
            A.sub_icdm,
            A.q_indices,
            A.q_distribution,
            A.c_As,
            B.distribution,
            B.sub_icdm,
            B.q_indices,
            B.q_distribution,
            B.c_As,
            init_cost,
        )

    P = sparse.coo_matrix((T_data, (T_rows, T_cols)), shape=(A.n, B.n)).tocsr()
    gw_loss = A.c_A + B.c_A - 2.0 * float(np.tensordot(A.icdm, P.dot(P.dot(B.icdm).T)))
    return P, sqrt(max(gw_loss, 0)) / 2.0


def _block_quantized_gw(indices):
    # Assumes that the global variable _QUANTIZED_CELLS has been declared, as by
    # init_qgw_pool
    (i0, i1), (j0, j1) = indices

    gw_list = []
    for i in range(i0, i1):
        A = _QUANTIZED_CELLS[i]
        for j in range(j0, j1):
            if i < j:
                B = _QUANTIZED_CELLS[j]
                gw_list.append((i, j, quantized_gw(A, B)))
    return gw_list


def _init_qgw_pool(quantized_cells: list[quantized_icdm]):
    """
    Initialize the parallel quantized GW computation by declaring a global variable
    accessible from all processes.
    """
    global _QUANTIZED_CELLS
    _QUANTIZED_CELLS = quantized_cells


def _quantized_gw_index(p: tuple[int, int]):
    """
    Given input p= (i,j), compute the quantized GW distance between cells i
    and j in the global list of quantized cells.
    """
    i, j = p
    retval : tuple[int,int,float]
    return (i, j, quantized_gw(_QUANTIZED_CELLS[i], _QUANTIZED_CELLS[j])[1])


def quantized_gw_parallel(
    intracell_csv_loc: str,
    num_processes: int,
    num_clusters: int,
    out_csv: str,
    chunksize: int = 20,
    verbose: bool = False,
    write_blocksize : int =100
) -> None:
    """
    Compute the quantized Gromov-Wasserstein distance in parallel between all cells in a family
    of cells.

    :param intracell_csv_loc: path to a CSV file containing the cells to process
    :param num_processes: number of Python processes to run in parallel
    :param num_clusters: Each cell will be partitioned into `num_clusters` many clusters.
    :param out_csv: file path where a CSV file containing
         the quantized GW distances will be written
    :param chunksize: How many q-GW distances should be computed at a time by each parallel process.
    """
    if verbose:
        print("Reading files...")
        cells = [cell for cell in tqdm(cell_iterator_csv(intracell_csv_loc))]
        names, cell_dms = zip(*cells)
        del cells
    else:
        names, cell_dms = zip(*cell_iterator_csv(intracell_csv_loc))
    if verbose:
        print("Quantizing intracell distance matrices...")
    with Pool(
        processes=num_processes
    ) as pool:
        args = [ (cell_dm, uniform(cell_dm.shape[0]) , num_clusters, None) for cell_dm in cell_dms ]
        quantized_cells = list(tqdm(pool.imap(quantized_icdm.of_tuple,args),total=len(names)))
    N = len(quantized_cells)
    total_num_pairs = int((N * (N - 1)) / 2)
    # index_pairs = tqdm(it.combinations(iter(range(N)), 2), total=total_num_pairs)
    index_pairs = it.combinations(iter(range(N)), 2)

    print("Computing pairwise Gromov-Wasserstein distances...")    
    with Pool(
        initializer=_init_qgw_pool, initargs=(quantized_cells,), processes=num_processes
    ) as pool:
        gw_dists = tqdm(
            pool.imap_unordered(
            _quantized_gw_index, index_pairs, chunksize=chunksize
            ),
            total = total_num_pairs)
        with open(out_csv, "w", newline="") as outcsvfile:
            csvwriter = csv.writer(outcsvfile)
            csvwriter.writerow(["first_object", "second_object", "quantized_gw"])
            for i,j,gw_dist in gw_dists:
                csvwriter.writerow((names[i],names[j],gw_dist))


def _cutoff_of(
    slb_dmat: npt.NDArray[np.float_],
    median: float,
    gw_dmat: npt.NDArray[np.float_],
    gw_known: npt.NDArray[np.bool_],
    nn: int,
) -> npt.NDArray[np.float_]:
    # maxval = np.max(gw_dmat)
    gw_copy = np.copy(gw_dmat)
    # gw_copy[~gw_known]=maxval
    gw_copy[~gw_known] = (slb_dmat + median)[~gw_known]
    gw_copy.partition(nn + 1, axis=1)
    return gw_copy[:, nn + 1]


def _tuple_iterator_of(
    X: npt.NDArray[np.int_], Y: npt.NDArray[np.int_]
) -> Iterator[tuple[int, int]]:
    b = set()
    for i, j in map(tuple, np.stack((X, Y), axis=1).astype(int)):
        if i < j:
            b.add((i, j))
        else:
            b.add((j, i))
    return iter(b)


def _get_indices(
    slb_dmat: npt.NDArray[np.float_],
    gw_dmat: npt.NDArray[np.float_],
    gw_known: npt.NDArray[np.bool_],
    accuracy: float,
    nearest_neighbors: int,
) -> list[tuple[int, int]]:
    """
    Based on the SLB distance matrix and the partially known GW distance matrix,
    and the desired accuracy, return a list of cell pairs which we should compute.
    This function does not return *all* cell pairs that must be computed for the desired accuracy;
    it is expected that the function will be called *repeatedly*, and that a new list of
    cell pairs will be given every time, roughly in descending order of priority;
    when the empty list is returned, this indicates that the gw distance
    table is already at the desired accuracy, and the loop should terminate.

    :param slb_dmat: the SLB distance matrix in squareform, but this would make sense for
    \any lower bound for gw_dmat
    :param gw_dmat: A partially defined
    Gromov-Wasserstein distance matrix in squareform, we should have
     gw_dmat >= slb_dmat almost everywhere where gw_known is true for this to make sense
    (I have not yet checked how this behaves in the case where some values of slb_dmat
    are greater than gw_dmat); should be zero elsewhere.
    :param gw_known: A matrix of Booleans which is true where the entries of `gw_dmat` are
    correct/valid and false where the entries are not meaningful/do not yet have the
    correct value
    :param accuracy: This is a real number between 0 and 1 inclusive. If the accuracy is 1,
    then pairwise cells will continue to be computed until all remaining uncomputed
    cell pairs have an SLB distance which is strictly higher than anything on the list of \
    `nearest_neighbors` many nearest neighbors of every point; thus the reported array of
    distances is guaranteed to be correct out to the first `nearest_neighbors` nearest neighbors
    of every point.
    """
    gw_vf = squareform(gw_dmat)
    N = gw_dmat.shape[0]
    bins = 200
    if np.all(gw_vf == 0.0):
        ind_y = np.argsort(slb_dmat, axis=1)[:, 1 : nearest_neighbors + 1]
        ind_x = np.broadcast_to(np.arange(N)[:, np.newaxis], (N, nearest_neighbors))
        xy = np.reshape(np.stack((ind_x, ind_y), axis=2), (-1, 2))
        return list(_tuple_iterator_of(xy[:, 0], xy[:, 1]))

    # Otherwise, we assume that at least the initial values have been computed.
    slb_vf = squareform(slb_dmat)

    errors = (gw_vf - slb_vf)[gw_vf > 0]
    error_quantiles = np.quantile(
        errors, np.arange(bins + 1).astype(float) / float(bins)
    )
    median = error_quantiles[int(bins / 2)]
    # cutoff = _cutoff_of(gw_dmat,gw_known,nearest_neighbors)
    cutoff = _cutoff_of(slb_dmat, median, gw_dmat, gw_known, nearest_neighbors)

    acceptable_injuries = (nearest_neighbors * N) * (1 - accuracy)
    # We want the expectation of injury to be below this.
    candidates = (~gw_known) & (slb_dmat <= cutoff[:, np.newaxis])
    X, Y = np.nonzero(candidates)
    candidate_count = X.shape[0]
    threshold = cutoff[X] - slb_dmat[X, Y]
    assert np.all(threshold >= 0)
    index_sort = np.argsort(threshold)
    quantiles = np.digitize(threshold, error_quantiles).astype(float) / float(bins)

    sq = np.sort(quantiles)
    K1 = int(np.searchsorted(np.cumsum(sq), acceptable_injuries))
    K2 = int(np.searchsorted(quantiles, 0.5))
    K = min(K1, K2)

    block_size = N * 5

    assert candidate_count == quantiles.shape[0]
    if K == quantiles.shape[0]:
        return []

    if (candidate_count - K) < block_size:
        from_index = K
    else:
        from_index = int((candidate_count + K) / 2)
        # from_index = candidate_count - block_size
        assert from_index >= K
        assert from_index < candidate_count
    indices = index_sort[from_index:]

    return list(_tuple_iterator_of(X[indices], Y[indices]))


def _update_dist_mat(
    gw_dist_iter: Iterable[tuple[int, int, float]],
    dist_mat: npt.NDArray[np.float_],
    dist_mat_known: npt.NDArray[np.bool_],
) -> None:
    """
    Write the values in `gw_dist_iter` to the matrix `dist_mat` and update the matrix
    `dist_mat_known` to reflect these known values.

    :param gw_dist_iter: An iterator over ordered triples (i,j,d) where i, j are array
    indices and d is a float.
    :param dist_mat: A distance matrix. The matrix is modified by this function;
    we set dist_mat[i,j]=d for all (i,j,d) in `gw_dist_iter`; similarly dist_mat[j,i]=d.
    :param dist_mat_known: An array of booleans recording what GW distances are known.
    This matrix is modified by this function.
    """
    for i, j, gw_dist in gw_dist_iter:
        dist_mat[i, j] = gw_dist
        dist_mat[j, i] = gw_dist
        dist_mat_known[i, j] = True
        dist_mat_known[j, i] = True
    return


def combined_slb_quantized_gw_memory(
    cell_dms: Collection[MetricMeasureSpace],  # Squareform
    num_processes: int,
    num_clusters: int,
    accuracy: float,
    nearest_neighbors: int,
    verbose: bool,
    chunksize: int = 20,
):
    """
    Estimate the qGW distance matrix for cells.

    Compute the pairwise SLB distances between each pair of cells in
    `cell_dms`.  Based on this initial estimate of the distances,
    compute the quantized GW distance between the nearest with
    `num_clusters` many clusters until the correct nearest-neighbors
    list is obtained for each cell with a high degree of confidence.

    The idea is that for the sake of clustering we can avoid
    computing the precise pairwise distances between cells which are far apart,
    because the clustering will not be sensitive to changes in large
    distances. Thus, we want to compute as precisely as possible the pairwise
    GW distances for (say) the 30 nearest neighbors of each point, and use a
    rough estimation beyond that.

    :param cell_dms: a list or tuple of square distance matrices
    :param num_processes: How many Python processes to run in parallel
    :param num_clusters: Each cell will be partitioned into `num_clusters` many
        clusters for the quantized Gromov-Wasserstein distance computation.
    :param chunksize: Number of pairwise cell distance computations done by
        each Python process at one time.
    :param out_csv: path to a CSV file where the results of the computation will be written
    :param accuracy: This is a real number between 0 and 1, inclusive.
    :param nearest_neighbors: The algorithm tries to compute only the
        quantized GW distances between pairs of cells if one is within the first
        `nearest_neighbors` neighbors of the other; for all other values,
        the SLB distance is used to give a rough estimate.
    """

    N = len(cell_dms)
    cells, cell_distributions = zip(*cell_dms)
    np_arange_N = np.arange(N)
    slb_dmat = slb_parallel_memory(cells, cell_distributions, num_processes, chunksize)

    # Partial quantized Gromov-Wasserstein table, will be filled in gradually.
    qgw_dmat = np.zeros((N, N), dtype=float)
    qgw_known = np.full(shape=(N, N), fill_value=False)
    qgw_known[np_arange_N, np_arange_N] = True

    quantized_cells = [
        quantized_icdm(
            cell_dm, cell_distribution, num_clusters
        )
        for cell_dm, cell_distribution in cell_dms
    ]
    # Debug
    total_cells_computed = 0
    with Pool(
        initializer=_init_qgw_pool, initargs=(quantized_cells,), processes=num_processes
    ) as pool:
        indices = _get_indices(
            slb_dmat, qgw_dmat, qgw_known, accuracy, nearest_neighbors
        )
        while len(indices) > 0:
            if verbose:
                print("Cell pairs computed so far: "
                      + str((np.count_nonzero(qgw_known) - N) / 2))
                print("Cell pairs to be computed this iteration: " + str(len(indices)))

            total_cells_computed += len(indices)
            qgw_dists = pool.imap_unordered(
                _quantized_gw_index, indices, chunksize=chunksize
            )
            _update_dist_mat(qgw_dists, qgw_dmat, qgw_known)
            assert np.count_nonzero(qgw_known) == 2 * total_cells_computed + N
            indices = _get_indices(
                slb_dmat, qgw_dmat, qgw_known, accuracy, nearest_neighbors
            )
    return slb_dmat, qgw_dmat, qgw_known


def combined_slb_quantized_gw(
    input_icdm_csv_location: str,
    gw_out_csv_location: str,
    num_processes: int,
    num_clusters: int,
    accuracy: float,
    nearest_neighbors: int,
    verbose: bool = False,
    chunksize: int = 20,
) -> None:
    """
    Estimate the qGW distance matrix for cells.

    This is a wrapper around :func:`cajal.qgw.combined_slb_quantized_gw_memory` with
    some associated file/IO. For all parameters not listed here see the docstring for
    :func:`cajal.qgw.combined_slb_quantized_gw_memory`.

    :param input_icdm_csv_location: file path to a csv file. For format for the icdm
        see :func:`cajal.run_gw.icdm_csv_validate`.
    :param gw_out_csv_location: Where to write the output GW distances.
    :return: None.
    """
    if verbose:
        print("Reading files...")
        names, cell_dms = zip(*tqdm(cell_iterator_csv(input_icdm_csv_location)))
    else:
        names, cell_dms = zip(*cell_iterator_csv(input_icdm_csv_location))
    mms = [(cell_dm, uniform(cell_dm.shape[0])) for cell_dm in cell_dms]
    slb_dmat, qgw_dmat, qgw_known = combined_slb_quantized_gw_memory(
        mms,
        num_processes,
        num_clusters,
        accuracy,
        nearest_neighbors,
        verbose,
        chunksize,
    )

    median_error = np.median((qgw_dmat - slb_dmat)[qgw_known])
    slb_estimator = slb_dmat + median_error
    qgw_dmat[~qgw_known] = slb_estimator[~qgw_known]
    ij = it.combinations(range(len(names)), 2)
    out = (
        (names[i], names[j], qgw_dmat[i, j], "QGW" if qgw_known[i, j] else "EST")
        for i, j in ij
    )
    batched_out = _batched(out, 1000)
    with open(gw_out_csv_location, "w", newline="") as outfile:
        csv_writer = csv.writer(outfile)
        for batch in batched_out:
            csv_writer.writerows(batch)

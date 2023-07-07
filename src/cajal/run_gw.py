"""
Functionality to compute Gromov-Wasserstein distances\
using algorithms in Peyre et al. ICML 2016
"""
# std lib dependencies
import itertools as it
import time
import csv
from typing import List, Iterable, Iterator, TypeVar, Optional, Collection
from math import sqrt, ceil


# external dependencies
import ot
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import squareform
from scipy import sparse
from scipy import cluster
from scipy.sparse import coo_array
from multiprocessing import Pool

from .slb import slb2 as slb2_cython
from .gw_cython import frobenius, quantized_gw_2

T = TypeVar("T")


def _batched(itera: Iterator[T], n: int) -> Iterator[List[T]]:
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    while batch := list(it.islice(itera, n)):
        yield batch


def _is_sorted(int_list: List[int]) -> bool:
    if len(int_list) <= 1:
        return True
    return all(map(lambda tup: tup[0] <= tup[1], zip(int_list[:-1], int_list[1:])))


def n_c_2(n: int):
    return (n * (n - 1)) // 2


def icdm_csv_validate(intracell_csv_loc: str) -> None:
    """
    Raise an exception if the file in intracell_csv_loc fails to pass formatting tests.
    """
    with open(intracell_csv_loc, "r", newline="") as icdm_infile:
        csv_reader = csv.reader(icdm_infile, delimiter=",")
        header = next(csv_reader)
        while header[0] == "#":
            header = next(csv_reader)
        if header[0] != "cell_id":
            raise ValueError("Expects header on first line starting with 'cell_id' ")
        linenum = 1
        for line in csv_reader:
            if line[0] == "#":
                continue
            try:
                float(line[1])
            except ValueError:
                print("Unexpected value at file line " + str(linenum) + ", token 2")
                raise

            line_length = len(header[1:])
            side_length = ceil(sqrt(2 * line_length))
            if side_length * (side_length - 1) != 2 * line_length:
                raise ValueError(
                    "Line " + str(linenum) + " is not in upper triangular form."
                )
            linenum += 1


def _batched_cell_list_iterator_csv(
    intracell_csv_loc: str, chunk_size: int
) -> Iterator[
    tuple[
        list[tuple[int, str, npt.NDArray[np.float_]]],
        list[tuple[int, str, npt.NDArray[np.float_]]],
    ]
]:
    """
    :param intracell_csv_loc: A full file path to a csv file.
    :param chunk_size: A size parameter.

    :return: An iterator over pairs (list1, list2), where each element \
    in list1 and list2 is a triple
    (cell_id, cell_name, icdm), where cell_id is a natural number,
    cell_name is a string, and icdm is a square n x n distance matrix.
    cell_id is guaranteed to be unique.

    Increasing chunk_size increases memory usage but reduces the frequency of file reads.

    Note that for parallelization concerns it is best to communicate large batches of work \
    to a child process at one time. However, numpy is already parallelizing the GW computations \
    under the hood so this is probably an irrelevant concern.
    """

    # Validate input
    icdm_csv_validate(intracell_csv_loc)

    with open(intracell_csv_loc, "r", newline="") as icdm_csvfile_outer:
        csv_outer_reader = enumerate(csv.reader(icdm_csvfile_outer, delimiter=","))
        _, first_line = next(csv_outer_reader)
        while first_line[0] == "#":
            _, first_line = next(csv_outer_reader)
        batched_outer = _batched(csv_outer_reader, chunk_size)
        for outer_batch in batched_outer:
            outer_list = [
                (
                    cell_id,
                    ell[0],
                    squareform(np.array([float(x) for x in ell[1:]], dtype=np.float_)),
                )
                for (cell_id, ell) in outer_batch
            ]
            first_outer_id = outer_list[0][0]
            print(first_outer_id)
            with open(intracell_csv_loc, newline="") as icdm_csvfile_inner:
                csv_inner_reader = enumerate(
                    csv.reader(icdm_csvfile_inner, delimiter=",")
                )
                while next(csv_inner_reader)[0] < first_outer_id:
                    pass
                batched_inner = _batched(csv_inner_reader, chunk_size)
                for inner_batch in batched_inner:
                    inner_list = [
                        (
                            cell_id,
                            ell[0],
                            squareform(
                                np.array([float(x) for x in ell[1:]], dtype=np.float64)
                            ),
                        )
                        for (cell_id, ell) in inner_batch
                    ]
                    yield outer_list, inner_list


def cell_iterator_csv(
    intracell_csv_loc: str,
) -> Iterator[tuple[str, npt.NDArray[np.float_]]]:
    """
    Return an iterator over cells in a directory. Intracell distance matrices are in squareform.
    """
    icdm_csv_validate(intracell_csv_loc)
    with open(intracell_csv_loc, "r", newline="") as icdm_csvfile:
        csv_reader = csv.reader(icdm_csvfile, delimiter=",")
        # Assume a header
        next(csv_reader)
        while ell := next(csv_reader, None):
            cell_name = ell[0]
            arr = squareform(
                np.array([float(x) for x in ell[1:]], dtype=np.float64),
                force="tomatrix",
            )
            yield cell_name, arr


def cell_pair_iterator_csv(
    intracell_csv_loc: str, chunk_size: int
) -> Iterator[
    tuple[
        tuple[int, str, npt.NDArray[np.float_]], tuple[int, str, npt.NDArray[np.float_]]
    ]
]:
    """
    Return an iterator over pairs of cells in a directory, of the form
    ((indexA, nameA, distance_matrixA),(indexB, nameB, distance_matrixB)).
    Intracell distance matrices are in squareform.
    """
    batched_it = _batched_cell_list_iterator_csv(intracell_csv_loc, chunk_size)
    return it.chain.from_iterable(
        (
            filter(lambda tup: tup[0][0] < tup[1][0], it.product(t1, t2))
            for t1, t2 in batched_it
        )
    )


def gw(fst_mat: npt.NDArray, snd_mat: npt.NDArray) -> float:
    """
    Readability/convenience wrapper for ot.gromov.gromov_wasserstein.

    :param A: Squareform distance matrix.
    :param B: Squareform distance matrix.
    :return: GW distance between them with square_loss optimization and \
    uniform distribution on points.
    """
    _, log = ot.gromov.gromov_wasserstein(
        fst_mat,
        snd_mat,
        ot.unif(fst_mat.shape[0]),
        ot.unif(snd_mat.shape[0]),
        "square_loss",
        log=True,
    )
    gw_dist = log["gw_dist"]
    # Should be unnecessary but floating point
    if gw_dist < 0:
        gw_dist = 0
    return sqrt(gw_dist) / 2.0


def _init_slb_worker(cells):
    """
    Declares a global list of distance matrices which can be accessed by child threads
    """
    global _VF_CELLS
    _VF_CELLS = cells


def _slb_by_indices(p: tuple[int, int]):
    """
    Used for parallelization, assumes that a global variable called _VF_CELLS has been
    declared (as in  _init_slb_worker)
    """
    i, j = p
    return (i, j, slb2_cython(_VF_CELLS[i], _VF_CELLS[j]))


def compute_slb2_distance_matrix(
    intracell_csv_loc: str,
    slb2_dist_csv_loc: str,
    num_processes: int,
    chunksize: int = 20,
    verbose: Optional[bool] = False,
) -> None:
    """
    Compute the pairwise slb2 distances between all intracell distance matrices
    in the file intracell_csv_loc.
    :param intracell_csv_loc: File path to an intracell distance matrix file.
    Same format as in `compute_gw_distance_matrix`.
    :param slb2_dist_csv_loc: Output file, where to write the slb2 distances.
    :param num_processes: How many Python processes to run in parallel.
    :param chunksize: How many jobs are fed to the child processes at one time.
    :param verbose: Prints timing information
    """
    start = time.time()
    names, cells = zip(
        *(
            (name, np.sort(squareform(cell)))
            for name, cell in cell_iterator_csv(intracell_csv_loc)
        )
    )
    N = len(cells)
    indices = it.combinations(iter(range(N)), 2)

    with Pool(
        processes=num_processes, initializer=_init_slb_worker, initargs=(cells,)
    ) as pool:
        slb_dists = pool.imap_unordered(_slb_by_indices, indices, chunksize=chunksize)
        with open(slb2_dist_csv_loc, "w", newline="") as outfile:
            csvwriter = csv.writer(outfile)
            stop = time.time()
            print("Init time: " + str(stop - start))
            start = time.time()
            for t in _batched(slb_dists, 2000):
                t = [(names[i], names[j], slb_dist) for i, j, slb_dist in t]
                csvwriter.writerows(t)
    stop = time.time()
    print("GW + File IO time " + str(stop - start))


def write_gw_dists(
    gw_dist_csv_loc: str,
    name_name_dist: Iterator[tuple[str, str, float]],
    verbose: Optional[bool] = False,
) -> None:
    """
    Given an iterator name_name_dist containing entries (cellA_name,cellB_name, gw_dist),
    writes these entries to a csv file.
    """
    chunk_size = 100
    counter = 0
    start = time.time()
    batched = _batched(name_name_dist, chunk_size)
    with open(gw_dist_csv_loc, "w", newline="") as gw_csv_file:
        csvwriter = csv.writer(gw_csv_file, delimiter=",")
        header = ["first_object", "second_object", "gw_dist"]
        csvwriter.writerow(header)
        for batch in batched:
            counter += len(batch)
            csvwriter.writerows(batch)
            now = time.time()
            if verbose:
                print("Time elapsed: " + str(now - start))
                print("Cell pairs computed: " + str(counter))
    stop = time.time()
    print(
        "Computation finished. Computed "
        + str(counter)
        + " cell pairs."
        + " Time elapsed: "
        + str(stop - start)
    )


def write_dists_and_coupling_mats(
    gw_dist_csv_loc: str,
    gw_coupling_mat_csv_loc: str,
    name_name_dist_coupling: Iterator[
        tuple[tuple[str, int, str, int, list[float]], tuple[str, str, float]]
    ],
    chunk_size: int = 500,
    verbose: Optional[bool] = False,
) -> None:
    """
    Given an iterator name_name_dist_coupling containing entries
    (first_object_name, first_object_sidelength, second_object_name,second_object_sidelength, ),
    writes these entries to a csv file.
    """

    counter = 0
    start = time.time()
    batched = _batched(name_name_dist_coupling, chunk_size)
    with open(gw_dist_csv_loc, "w", newline="") as gw_dist_csv_file, open(
        gw_coupling_mat_csv_loc, "w", newline=""
    ) as gw_coupling_mat_csv_file:
        dist_writer = csv.writer(gw_dist_csv_file, delimiter=",")
        coupling_writer = csv.writer(gw_coupling_mat_csv_file, delimiter=",")
        dist_header = ["first_object", "second_object", "gw_dist"]
        dist_writer.writerow(dist_header)
        coupling_header = [
            "first_object",
            "first_object_sidelength",
            "second_object",
            "second_object_sidelength",
            "num_non_zero",
            "coupling",
        ]
        coupling_writer.writerow(coupling_header)
        for batch in batched:
            couplings, dists = [list(tup) for tup in zip(*batch)]
            couplings = [
                [A_name, A_sidelength, B_name, B_sidelength] + coupling_mat
                for (
                    A_name,
                    A_sidelength,
                    B_name,
                    B_sidelength,
                    coupling_mat,
                ) in couplings
            ]
            counter += len(batch)
            dist_writer.writerows(dists)
            coupling_writer.writerows(couplings)
            now = time.time()
            if verbose:
                print("Time elapsed: " + str(now - start))
                print("Cell pairs computed: " + str(counter))
    stop = time.time()
    print(
        "Computation finished. Computed "
        + str(counter)
        + " many cell pairs."
        + " Time elapsed: "
        + str(stop - start)
    )


def _coupling_mat_reformat(coupling_mat: npt.NDArray[np.float_]) -> list[float | int]:
    """
    Convert a sparse coupling matrix to something that can be written to a csv file.
    """
    return [x for ell in coupling_mat for x in ell]
    coo = coo_array(coupling_mat)
    ell = [coo.nnz]
    ell += list(coo.data)
    ell += list(coo.row)
    ell += list(coo.col)
    return ell


def _gw_dist_coupling(
    cellA_name: str,
    cellA_icdm: npt.NDArray[np.float_],
    cellB_name: str,
    cellB_icdm: npt.NDArray[np.float_],
) -> tuple[tuple[str, int, str, int, list[float]], tuple[str, str, float]]:
    """
    Compute the Gromov-Wasserstein distance between two cells, and return
    this information along with other context in a manner which is immediately
    suitable for being written to a text file.
    """
    cellA_sidelength = cellA_icdm.shape[0]
    cellB_sidelength = cellB_icdm.shape[0]
    coupling_mat, log = ot.gromov.gromov_wasserstein(
        cellA_icdm,
        cellB_icdm,
        ot.unif(cellA_sidelength),
        ot.unif(cellB_sidelength),
        "square_loss",
        log=True,
    )
    coupling_mat = _coupling_mat_reformat(coupling_mat)
    gw_dist = log["gw_dist"]
    # This should be unnecessary but floating point reasons
    if gw_dist < 0:
        gw_dist = 0
    return (cellA_name, cellA_sidelength, cellB_name, cellB_sidelength, coupling_mat), (
        cellA_name,
        cellB_name,
        sqrt(gw_dist) / 2.0,
    )


def compute_gw_distance_matrix(
    intracell_csv_loc: str,
    gw_dist_csv_loc: str,
    gw_coupling_mat_csv_loc: Optional[str] = None,
    verbose: Optional[bool] = False,
) -> None:
    """
    :param intracell_csv_loc: A file containing the intracell distance matrices
    for all cells.

    :param gw_dist_csv_loc: An output file containing the Gromov-Wasserstein
    distances, which will be created if it does not exist and overwritten if it
    does.

    :param gw_coupling_mat_csv_loc: If this argument is not None, for each pair
    of cells, the coupling matrices will be retained and written to this output
    file. If this argument is None, the coupling matrices will be discarded. Be
    warned that the coupling matrices are large.
    """
    chunk_size = 100
    cell_pairs = cell_pair_iterator_csv(intracell_csv_loc, chunk_size)

    if gw_coupling_mat_csv_loc is not None:
        write_data = (
            _gw_dist_coupling(cellA_name, cellA_icdm, cellB_name, cellB_icdm)
            for (_, cellA_name, cellA_icdm), (_, cellB_name, cellB_icdm) in cell_pairs
        )
        write_dists_and_coupling_mats(
            gw_dist_csv_loc, gw_coupling_mat_csv_loc, write_data, verbose=verbose
        )
    else:
        write_dists = (
            (cellA_name, cellB_name, gw(cellA_icdm, cellB_icdm))
            for (_, cellA_name, cellA_icdm), (_, cellB_name, cellB_icdm) in cell_pairs
        )
        write_gw_dists(gw_dist_csv_loc, write_dists, verbose=verbose)


class quantized_icdm:
    """
    This class represents a "quantized" intracell distance matrix, i.e.,
    a metric measure space which has been equipped with a given clustering;
    it contains additional data which allows for the rapid computation
    of pairwise GW distances across many cells.
    """

    n: int
    # 2 dimensional square matrix of side length n.
    icdm: npt.NDArray[np.float64]
    # "distribution" is a dimensional vector of length n,
    # a probability distribution on points of the space
    distribution: npt.NDArray[np.float64]
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

    def __init__(
        self,
        cell_dm: npt.NDArray[np.float64],
        p: npt.NDArray[np.float64],
        num_clusters: int,
    ):
        """
        :param cell_dm: An intracell distance matrix in squareform.
        :param p: A probability distribution on the points of the metric space
        :param num_clusters: How many clusters to subdivide the cell into; the more clusters,
        the more accuracy, but the longer the computation.
        """
        assert len(cell_dm.shape) == 2
        self.n = cell_dm.shape[0]
        cell_dm_sq = np.multiply(cell_dm, cell_dm)
        self.c_A = np.dot(np.dot(cell_dm_sq, p), p)
        Z = cluster.hierarchy.linkage(squareform(cell_dm), method="centroid")
        clusters = cluster.hierarchy.fcluster(
            Z, num_clusters, criterion="maxclust", depth=0
        )
        actual_num_clusters: int = len(set(clusters))
        self.ns = actual_num_clusters
        indices: npt.NDArray[np.int_] = np.argsort(clusters)
        original_cell_dm = cell_dm
        cell_dm = cell_dm[indices, :][:, indices]
        p = p[indices]
        q: list[float]
        q = []
        clusters = np.sort(clusters)
        for i in range(1, actual_num_clusters + 1):
            permutation = np.nonzero(clusters == i)[0]
            this_cluster = cell_dm[permutation, :][:, permutation]
            medoid = np.argmin(sum(this_cluster))
            new_local_indices = np.argsort(this_cluster[medoid])
            cell_dm[permutation, :] = cell_dm[permutation[new_local_indices], :]
            cell_dm[:, permutation] = cell_dm[:, permutation[new_local_indices]]
            indices[permutation] = indices[permutation[new_local_indices]]
            p[permutation] = p[permutation[new_local_indices]]
            q.append(np.sum(p[permutation]))
        self.icdm = np.asarray(cell_dm, order="C")
        self.distribution = p
        q_arr = np.array(q, dtype=np.float64, order="C")
        self.q_distribution = q_arr
        assert abs(np.sum(q_arr) - 1.0) < 1e-7
        medoids = np.nonzero(np.r_[1, np.diff(clusters)])[0]
        A_s = cell_dm[medoids, :][:, medoids]
        assert np.all(np.equal(original_cell_dm[:, indices][indices, :], cell_dm))
        self.sub_icdm = np.asarray(A_s, order="C")
        self.q_indices = np.asarray(
            np.nonzero(np.r_[1, np.diff(clusters), 1])[0], order="C"
        )
        self.c_As = np.dot(np.multiply(A_s, A_s), q_arr) @ q_arr
        self.A_s_a_s = np.dot(A_s, q_arr)


def quantized_gw(A: quantized_icdm, B: quantized_icdm):
    """
    Compute the quantized Gromov-Wasserstein distance between two quantized metric measure spaces.
    """
    T_rows, T_cols, T_data = quantized_gw_2(
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

    P = sparse.coo_matrix((T_data, (T_rows, T_cols)), shape=(A.n, B.n)).tocsr()
    gw_loss = A.c_A + B.c_A - 2.0 * frobenius(A.icdm, P.dot(P.dot(B.icdm).T))
    return sqrt(gw_loss) / 2.0


def _block_quantized_gw(indices):
    # Assumes that the global variable _QUANTIZED_CELLS has been declared, as by
    # init_pool
    (i0, i1), (j0, j1) = indices

    gw_list = []
    for i in range(i0, i1):
        A = _QUANTIZED_CELLS[i]
        for j in range(j0, j1):
            if i < j:
                B = _QUANTIZED_CELLS[j]
                gw_list.append((i, j, quantized_gw(A, B)))
    return gw_list


def _init_pool(quantized_cells: list[quantized_icdm]):
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
    return (i, j, quantized_gw(_QUANTIZED_CELLS[i], _QUANTIZED_CELLS[j]))


def quantized_gw_parallel(
    intracell_csv_loc: str,
    num_processes: int,
    num_clusters: int,
    out_csv: str,
    chunksize: int = 20,
    verbose: bool = False,
):
    """
    Compute the quantized Gromov-Wasserstein distance in parallel between all cells in a family
    of cells.
    :param intracell_csv_loc: path to a CSV file containing the cells to process
    :param num_processes: number of Python processes to run in parallel
    :param num_clusters: Each cell will be partitioned into `num_clusters` many clusters.
    :out_csv: file path where a CSV file containing the quantized GW distances will be written
    :chunksize: How many q-GW distances should be computed at a time by each parallel process.
    """
    names, cell_dms = zip(*cell_iterator_csv(intracell_csv_loc))
    quantized_cells = [
        quantized_icdm(
            cell_dm, np.ones((cell_dm.shape[0],)) / cell_dm.shape[0], num_clusters
        )
        for cell_dm in cell_dms
    ]
    N = len(quantized_cells)
    index_pairs = it.combinations(iter(range(N)), 2)

    gw_time = 0.0
    fileio_time = 0.0
    gw_start = time.time()
    with Pool(
        initializer=_init_pool, initargs=(quantized_cells,), processes=num_processes
    ) as pool:
        gw_dists = pool.imap_unordered(
            _quantized_gw_index, index_pairs, chunksize=chunksize
        )
        gw_stop = time.time()
        gw_time += gw_stop - gw_start
        with open(out_csv, "w", newline="") as outcsvfile:
            csvwriter = csv.writer(outcsvfile)
            gw_start = time.time()
            t = _batched(gw_dists, 2000)
            for block in t:
                block = [(names[i], names[j], gw_dist) for (i, j, gw_dist) in block]
                gw_stop = time.time()
                gw_time += gw_stop - gw_start
                csvwriter.writerows(block)
                gw_start = time.time()
                fileio_time += gw_start - gw_stop


def _init_slb2_pool(sorted_cells):
    """
    Initialize the parallel SLB computation by declaring a global variable
    accessible from all processes.
    """

    global _SORTED_CELLS
    _SORTED_CELLS = sorted_cells


def _global_slb2_pool(p: tuple[int, int]):
    """
    Given input p= (i,j), compute the SLB distance between cells i
    and j in the global list of cells.
    """

    i, j = p
    return (i, j, slb2_cython(_SORTED_CELLS[i], _SORTED_CELLS[j]))


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


def slb_parallel(
    cell_dms: Collection[npt.NDArray[np.float_]],
    num_processes: int,
    chunksize: int = 20,
) -> npt.NDArray[np.float_]:
    """
    Compute the SLB distance in parallel between all cells in `cell_dms`.
    :param cell_dms: A collection of distance matrices
    :param num_processes: How many Python processes to run in parallel
    :param chunksize: How many SLB distances each Python process computes at a time
    """
    cell_dms_sorted = [np.sort(squareform(cell, force="tovector")) for cell in cell_dms]
    N = len(cell_dms)
    with Pool(
        initializer=_init_slb2_pool,
        initargs=(cell_dms_sorted,),
        processes=num_processes,
    ) as pool:
        slb2_dists = pool.imap_unordered(
            _global_slb2_pool, it.combinations(iter(range(N)), 2), chunksize=chunksize
        )
        arr = np.zeros((N, N))
        for i, j, x in slb2_dists:
            arr[i, j] = x
            arr[j, i] = x

    return arr


def _get_indices(
    slb_dmat: npt.NDArray[np.float_],
    gw_dmat: npt.NDArray[np.float_],
    gw_known: npt.NDArray[np.int_],
    confidence_parameter: float,
    nearest_neighbors: int,
) -> tuple[list[tuple[int, int]], npt.NDArray[np.float_]]:
    gw_vf = squareform(gw_dmat)
    slb_vf = squareform(slb_dmat)
    errors = (gw_vf - slb_vf)[gw_vf > 0]
    if errors.shape[0] == 0:
        estimator_dmat = np.copy(slb_dmat)
    else:
        acceptable_error = (
            0
            if confidence_parameter == 0
            else np.quantile(errors, confidence_parameter)
        )
        estimator_dmat = squareform(slb_vf + acceptable_error)
        gw_known_x, gw_known_y = np.nonzero(gw_known)
        estimator_dmat[gw_known_x, gw_known_y] = gw_dmat[gw_known_x, gw_known_y]

    cutoff = np.partition(estimator_dmat, nearest_neighbors + 1)[
        :, nearest_neighbors + 1
    ]
    X: npt.NDArray[np.int_]
    Y: npt.NDArray[np.int_]
    X, Y = np.nonzero((estimator_dmat <= cutoff[:, np.newaxis]) & (~gw_known))
    indices = zip(*(X, Y))
    reduced_indices = list(set(((i, j) if i < j else (j, i) for i, j in indices)))
    return reduced_indices, estimator_dmat


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
    gw_copy[~gw_known] = (slb_dmat)[~gw_known]
    gw_copy.partition(nn + 1, axis=1)
    return gw_copy[:, nn + 1]


def _tuple_iterator_of(
    X: npt.NDArray[np.int_], Y: npt.NDArray[np.int_]
) -> Iterator[tuple[int, int]]:
    b = set()
    for i, j in map(tuple, np.stack((X, Y), axis=1, dtype=int).astype(int)):
        if i < j:
            b.add((i, j))
        else:
            b.add((j, i))
    return iter(b)


# def sort_by_threshold_likelihood(
#         slb_dmat: npt.NDArray[np.float_],
#         gw_dmat: npt.NDArray[np.float_],
#         gw_known: npt.NDArray[np.bool_],
#         accuracy : float,
#         nearest_neighbors: int):


def _get_indices_v2(
    slb_dmat: npt.NDArray[np.float_],
    gw_dmat: npt.NDArray[np.float_],
    gw_known: npt.NDArray[np.bool_],
    accuracy: float,
    nearest_neighbors: int,
) -> list[tuple[int, int]]:
    gw_vf = squareform(gw_dmat)
    N = gw_dmat.shape[0]
    bins = 200
    if np.all(gw_vf == 0.0):
        ind_y = np.argsort(slb_dmat, axis=1)[:, 1 : nearest_neighbors + 1]
        ind_x = np.broadcast_to(np.arange(N)[:, np.newaxis], (N, nearest_neighbors))
        xy = np.reshape(np.stack((ind_x, ind_y), axis=2, dtype=int), (-1, 2))
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

    K = int(np.searchsorted(np.cumsum(np.sort(quantiles)), acceptable_injuries))

    assert candidate_count == quantiles.shape[0]
    if K == quantiles.shape[0]:
        return []

    if (candidate_count - K) < 1000:
        from_index = K
        # indices=index_sort[K:]
    else:
        # from_index = int((candidate_count + K)/2)
        from_index = candidate_count - 1000
        # assert from_index >= K
        # assert from_index < candidate_count
    indices = index_sort[from_index:]

    return list(_tuple_iterator_of(X[indices], Y[indices]))


def combined_slb2_quantized_gw_memory(
    cell_dms: Collection[npt.NDArray[np.float_]],  # Squareform
    num_processes: int,
    num_clusters: int,
    confidence_parameter: float,
    nearest_neighbors: int,
    verbose: bool,
    chunksize: int = 20,
):
    """
    Compute the pairwise SLB distances between each pair of cells in `cell_dms`.
    Based on this initial estimate of the distances, compute the quantized GW distance between
    the nearest with `num_clusters` many clusters until the correct nearest-neighbors list is
    obtained for each cell with a high degree of confidence.

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
    :confidence_parameter: This is a real number between 0 and 1, inclusive.
    If `confidence_parameter ==0`, then there is a 100% chance that the correct nearest
    neighbors list is obtained. If ``confidence_parameter == 0.05`, then for each cell in
    the reported list of nearest neighbors, we estimate at most a 5% chance
    that this cell is not actually in the list of nearest neighbors.
    :param nearest_neighbors: The algorithm tries to compute only the
    quantized GW distances between pairs of cells if one is within the first
    `nearest_neighbors` neighbors of the other; for all other values,
    the SLB distance is used to give a rough estimate.
    """

    N = len(cell_dms)
    np_arange_N = np.arange(N)
    slb2_dmat = slb_parallel(cell_dms, num_processes, chunksize)

    # Partial quantized Gromov-Wasserstein table, will be filled in gradually.
    qgw_dmat = np.zeros((N, N), dtype=float)
    qgw_known = np.full(shape=(N, N), fill_value=False)
    qgw_known[np_arange_N, np_arange_N] = True

    quantized_cells = [
        quantized_icdm(
            cell_dm, np.ones((cell_dm.shape[0],)) / cell_dm.shape[0], num_clusters
        )
        for cell_dm in cell_dms
    ]
    # Debug
    total_cells_computed = 0
    with Pool(
        initializer=_init_pool, initargs=(quantized_cells,), processes=num_processes
    ) as pool:
        indices, estimator_dmat = _get_indices(
            slb2_dmat, qgw_dmat, qgw_known, confidence_parameter, nearest_neighbors
        )
        while len(indices) > 0:
            if verbose:
                print(len(indices))
            total_cells_computed += len(indices)
            qgw_dists = pool.imap_unordered(
                _quantized_gw_index, indices, chunksize=chunksize
            )
            _update_dist_mat(qgw_dists, qgw_dmat, qgw_known)
            assert np.count_nonzero(qgw_known) == 2 * total_cells_computed + N
            indices, estimator_dmat = _get_indices(
                slb2_dmat, qgw_dmat, qgw_known, confidence_parameter, nearest_neighbors
            )
    return slb2_dmat, qgw_dmat, qgw_known, estimator_dmat


# In this version of the algorithm, the user supplies an accuracy parameter between 0 and 1.
def combined_slb2_quantized_gw_memory_v2(
    cell_dms: Collection[npt.NDArray[np.float_]],  # Squareform
    num_processes: int,
    num_clusters: int,
    accuracy: float,
    nearest_neighbors: int,
    verbose: bool,
    chunksize: int = 20,
):
    """
    Compute the pairwise SLB distances between each pair of cells in `cell_dms`.
    Based on this initial estimate of the distances, compute the quantized GW distance between
    the nearest with `num_clusters` many clusters until the correct nearest-neighbors list is
    obtained for each cell with a high degree of confidence.

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
    :accuracy: This is a real number between 0 and 1, inclusive.
    :param nearest_neighbors: The algorithm tries to compute only the
    quantized GW distances between pairs of cells if one is within the first
    `nearest_neighbors` neighbors of the other; for all other values,
    the SLB distance is used to give a rough estimate.
    """

    N = len(cell_dms)
    np_arange_N = np.arange(N)
    slb2_dmat = slb_parallel(cell_dms, num_processes, chunksize)

    # Partial quantized Gromov-Wasserstein table, will be filled in gradually.
    qgw_dmat = np.zeros((N, N), dtype=float)
    qgw_known = np.full(shape=(N, N), fill_value=False)
    qgw_known[np_arange_N, np_arange_N] = True

    quantized_cells = [
        quantized_icdm(
            cell_dm, np.ones((cell_dm.shape[0],)) / cell_dm.shape[0], num_clusters
        )
        for cell_dm in cell_dms
    ]
    # Debug
    total_cells_computed = 0
    with Pool(
        initializer=_init_pool, initargs=(quantized_cells,), processes=num_processes
    ) as pool:
        indices = _get_indices_v2(
            slb2_dmat, qgw_dmat, qgw_known, accuracy, nearest_neighbors
        )
        while len(indices) > 0:
            if verbose:
                print(len(indices))
            total_cells_computed += len(indices)
            qgw_dists = pool.imap_unordered(
                _quantized_gw_index, indices, chunksize=chunksize
            )
            _update_dist_mat(qgw_dists, qgw_dmat, qgw_known)
            assert np.count_nonzero(qgw_known) == 2 * total_cells_computed + N
            indices = _get_indices_v2(
                slb2_dmat, qgw_dmat, qgw_known, accuracy, nearest_neighbors
            )
    return slb2_dmat, qgw_dmat, qgw_known


def combined_slb2_quantized_gw(
    intracell_csv_loc: str,
    num_processes: int,
    num_clusters: int,
    out_csv: str,
    confidence_parameter: float,
    nearest_neighbors: int,
    verbose: bool,
    chunksize: int = 20,
):
    """
    Compute the pairwise SLB distances between each pair of cells in `intracell_csv_loc`.
    Based on this initial estimate of the distances, compute the quantized GW distance between
    the nearest with `num_clusters` many clusters until the correct nearest-neighbors list is
    obtained for each cell with a high degree of confidence.

    The idea is that for the sake of clustering we can avoid
    computing the precise pairwise distances between cells which are far apart,
    because the clustering will not be sensitive to changes in large
    distances. Thus, we want to compute as precisely as possible the pairwise
    GW distances for (say) the 30 nearest neighbors of each point, and use a
    rough estimation beyond that.

    :param intracell_csv_loc: path to a CSV file containing the cells to process
    :param num_processes: How many Python processes to run in parallel
    :param num_clusters: Each cell will be partitioned into `num_clusters` many
    clusters for the quantized Gromov-Wasserstein distance computation.
    :param chunksize: Number of pairwise cell distance computations done by
    each Python process at one time.
    :param out_csv: path to a CSV file where the results of the computation will be written
    :confidence_parameter: This is a real number between 0 and 1, inclusive.
    If `confidence_parameter ==0`, then there is a 100% chance that the correct nearest
    neighbors list is obtained. If ``confidence_parameter == 0.05`, then for each cell in
    the reported list of nearest neighbors, we estimate at most a 5% chance
    that this cell is not actually in the list of nearest neighbors.
    :param nearest_neighbors: The algorithm tries to compute only the
    quantized GW distances between pairs of cells if one is within the first
    `nearest_neighbors` neighbors of the other; for all other values,
    the SLB distance is used to give a rough estimate.
    """
    names, cell_dms = zip(*cell_iterator_csv(intracell_csv_loc))
    N = len(names)
    slb2_dmat, qgw_dmat, qgw_known, estimator_dmat = combined_slb2_quantized_gw_memory(
        cell_dms,
        num_processes,
        num_clusters,
        confidence_parameter,
        nearest_neighbors,
        verbose,
        chunksize,
    )

    with open(out_csv, "w", newline="") as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["name1", "name2", "dist", "type"])
        ij = it.combinations(range(N), 2)
        rows = (
            (
                names[i],
                names[j],
                estimator_dmat[i, j],
                "QGW" if qgw_known[i, j] else "SLB",
            )
            for i, j in ij
        )
        csv_writer.writerows(rows)

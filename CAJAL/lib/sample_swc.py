# Functions for sampling even points from an SWC reconstruction of a neuron
import re
import numpy as np
# import numpy.typing as npt      
from CAJAL.lib.utilities import pj
from scipy.spatial.distance import euclidean, squareform
import networkx as nx
import warnings
from typing import List, Dict, Tuple, Optional, Iterable, Set
from multiprocessing import Pool
# import time
import os

# TODO - stylistic change. Once we are ready to increase the minimum supported
# version of Python to >= 3.9, these should be changed from uppercase Tuple,
# Dict, List to lowercase tuple, dict, list etc.
StructureID = int
CoordTriple = Tuple[float,float,float]
NeuronNode = Tuple[StructureID,CoordTriple]
NodeIndex = int
# A ComponentTree is a directed graph formatted as a dictionary, where each node contains the key of its parent.
# Our convention will be that the component_tree[0] is always the root.
ComponentTree = Dict[NodeIndex, Tuple[NeuronNode,NodeIndex]] 
SWCData = List[ComponentTree]

def read_SWCData(file_path : str, keep_disconnect) -> SWCData:
    """
    Reads an SWC file and returns a representation of the data as a list of the connected components of the neuron.    

    The SWC file should conform to the documentation here: www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html

    Args:
        file_path (string): absolute path to SWC file.
    Returns:
        list of connected components of the neurons.
    """

    swc_data : SWCData = []
    # component_dict : Dict[NodeIndex,ComponentTree] = [] 
    # core_dict : Optional[ComponentTree] = None
    
    with open(file_path, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            row = re.split("\s|\t", line.strip())[0:7]
            if len(row) < 7:
                raise TypeError("Row" + line + "in file" + file_path + "has fewer than seven whitespace-separated strings.")
            node_index, structure_id = int(row[0]), int(row[1])
            x, y, z = float(row[2]), float(row[3]), float(row[4])
                      # Radius discarded
            parent_id = int(row[6])
            if parent_id == -1:
                root_node : NeuronNode = (structure_id, (x, y, z))
                swc_data.append( { node_index : (root_node,-1) } )
            else:
                my_dict : Optional[ComponentTree] = None
                for d in swc_data:
                    if parent_id in d.keys():
                        my_dict = d
                        break
                if my_dict is None:
                    raise ValueError("SWC parent nodes must be listed before the child node that references them. The node with index "
                                     + row[0] + " was accessed before its parent "+ row[6])
                my_dict[node_index]=((structure_id, (x,y,z)),parent_id)
        return swc_data

def read_swc(file_path : str) -> List[List[str]]:
    """
    Reads an SWC file and returns a list of the non-comment lines, split by spaces into tokens.

    The SWC file should conform to the documentation here: http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html

    In particular, all rows should be either a comment starting with the character "#" or should have at least seven strings separated by whitespace.
    
    read_swc(file_path)[i] is the i-th non-comment row, split into a list of strings by whitespace.

    If there are fewer than seven whitespace-separated tokens in the i-th row, an error is raised.

    If there are greater than seven whitespace-separated tokens in the i-th row, the first seven tokens are kept and the rest discarded.

    The seventh token is assumed to be the parent node index and to be -1 if the node has no parent.

    read_swc expects the rows of the graph to be in topologically sorted order (parents before children) If this is not satisfied, read_swc raises an exception.
    In particular, the first node must be the root of the tree, and its parent has index -1.
        
    Args:
        file_path (string): absolute path to SWC file

    Returns:
        list of vertex rows from SWC file, where each vertex row is a list of eight strings.
    """
    vertices = []
    ids : Set[str] = set()
    ids.add("-1")
    with open(file_path, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            row = re.split("\s|\t", line.strip())[0:7]
            if len(row) < 7:
                raise TypeError("Row" + line + "in file" + file_path + "has fewer than eight whitespace-separated strings.")
            if row[6] not in ids:
                raise ValueError("SWC parent nodes must be listed before the child node that references them. The node with index "
                                 + row[0] + " was accessed before its parent "+ row[6])
            ids.add(row[0])
            vertices.append(row)
    return vertices

def prep_coord_dict(vertices : List[List[str]],
                    types_keep : Optional[Iterable[int]] = None,
                    keep_disconnect=False) -> Tuple[List[List[str]], Dict[int,np.ndarray], float]:
    """
    Read through swc file list, get dictionary of vertex coordinates and total length of all segments

    Args:
        vertices (list): list of vertex rows from SWC file
        types_keep (tuple,list): list of SWC neuron part types to sample points from. By default, uses all points.
    Only points 
        keep_disconnect (boolean): If False, will only keep branches connected to the soma.
            If True, will keep all branches, including free-floating ones

    Returns:
        vertices_keep: list of rows from SWC file that are connected to the soma
        vertex_coords: dictionary of xyz coordinates for the ID of each vertex in vertices_keep
        total_length: sum of segment lengths from branches of kept vertices
    """
    # in case types_keep are numbers
    types_keep_strings : Optional[List[str]] = None
    if types_keep is not None:
        types_keep_strings = [str(x) for x in types_keep]

    vertices_keep : List[List[str]] = []
    vertex_coords : Dict[int,np.ndarray] = {}
    total_length : float = 0
    for v in vertices:
        this_id = int(v[0])
        this_coord = np.array((float(v[2]), float(v[3]), float(v[4])))
        pid = int(v[-1])
        if pid < 0:
            # If not keeping disconnected parts, only keep vertex without parent
            # if it has soma type or is first vertex
            if keep_disconnect or v[1] == "1" or len(vertices_keep) == 0:
                vertex_coords[this_id] = this_coord
                vertices_keep.append(v)
        elif pid in vertex_coords.keys():
            # keep branch vertex if connected to soma root
            vertex_coords[this_id] = this_coord
            vertices_keep.append(v)
            seg_len = euclidean(vertex_coords[pid], this_coord)
            if types_keep_strings is None or v[1] in types_keep_strings:
                total_length += seg_len
        elif types_keep_strings is not None and v[1] in types_keep_strings:
            raise ValueError(
                "Vertex " + v[0] +" is of type "+ v[1] +
                " which is in the list of types to keep, but its\
                parent may not be. CAJAL does not currently have a\
                strategy to deal with such SWC files. \
                Suggest cleaning the data or setting \
                types_keep = None.")
            
    return vertices_keep, vertex_coords, total_length

def sample_pts_step(vertices : List[List[str]], vertex_coords: Dict[int,np.ndarray],
                    step_size : float,
                    types_keep: Optional[Iterable[int]] = None) -> Tuple[List[np.ndarray],int]:
    """
    Sample points at every set interval (step_size) along branches of neuron

    Args:
        vertices (list): list of rows from SWC file that are connected to the soma
        vertex_coords (dict): dictionary of xyz coordinates for the ID of each vertex in vertices_keep
        step_size (float): even distance to sample points radially from soma
        types_keep (tuple,list): list of SWC neuron part types to sample points from
            by default, uses only 1 (soma), 2 (axon), 3 (basal dendrite), 4 (apical dendrite)

    Returns:
        sampled_pts_list: list of xyz coordinates for sampled points
        num_roots: number of connected parts of neuron
    """
    
    # The implementation of this function constructs a new graph (forest) T on
    # top of the input graph (forest), G, where G is sampled from the SWC
    # file. The nodes of T lie on the geometric line segments connecting the
    # nodes of G. Every node of T is of the form ax+by,
    # where x and y are nodes of G with x the parent of y, and a, b
    # are real coefficients with a, b >=0 and a+b == 1. The parent node of a
    # node in T is the next nearest node along the path to the root of that tree. T is
    # constructed so that the geodesic distance between a parent and child node is exactly step_size.
    
    # The keys of vertex_dist are nodes in G.  The value vertex_dist[v] is a
    # float, which is the geodesic distance between v and the nearest node
    # above it in T, say x. Note that if step_size < dist(v,parent(v)), then x
    # will lie on the line segment between v and parent(v); however, if
    # step_size >> dist(v, parent(v)), then there may be several nodes of G
    # between v and x.
    vertex_dist : Dict[int,float] = {}

    # The list of nodes of T, represented as numpy float arrays of length 3.
    sampled_pts_list : List[np.ndarray] = []

    # The number of connected components of the forest.
    num_roots : int = 0

    types_keep_strings : Optional[List[str]]= None
    # in case types_keep are numbers
    if types_keep is not None:
        types_keep_strings = [str(x) for x in types_keep] if isinstance(types_keep, Iterable) else [str(types_keep)]
    
    # loop through list of vertices, sampling points from edge of vertex to parent
    for v in vertices:
        this_id = int(v[0])
        this_coord = np.array((float(v[2]), float(v[3]), float(v[4])))
        pid = int(v[-1])
        if pid == -1:
            num_roots += 1
            vertex_dist[this_id] = 0
            sampled_pts_list.append(this_coord)
            continue
        seg_len = euclidean(vertex_coords[pid], this_coord)
        pts_dist = np.arange(step_size, seg_len + vertex_dist[pid], step_size)
        if (types_keep_strings is None or v[1] in types_keep_strings) and len(pts_dist) > 0:
            pts_dist = pts_dist - vertex_dist[pid]
            new_dist = seg_len - pts_dist[-1]
            new_pts = [vertex_coords[pid] + (this_coord - vertex_coords[pid]) * x / seg_len for x in pts_dist]
            if types_keep_strings is None or v[1] in types_keep_strings:
                sampled_pts_list.extend(new_pts)
            vertex_dist[this_id] = new_dist
        else:
            vertex_dist[this_id] = vertex_dist[pid] + seg_len
    return sampled_pts_list, num_roots


def sample_n_pts(vertices : List[List[str]], vertex_coords : Dict[int,np.ndarray],
                 total_length : float, types_keep : Optional[Iterable[int]] = None,
                 goal_num_pts : int =50, min_step_change : float =1e-7,
                 max_iters : int =50,
                 verbose : bool =False) -> Optional[Tuple[np.ndarray,int,float,int]]:
    """
    Use binary search to find step size between points that will sample the required number of points

    Args:
        vertices (list): list of tokenized rows from SWC file that are connected to the soma
        vertex_coords (dict): dictionary of xyz coordinates for the ID of each vertex in vertices_keep
        total_length (float): sum of segment lengths from branches of kept vertices
        types_keep: list of SWC neuron part types to sample points from.
            By default, all points are kept. The standard structure identifiers are 1-4, with 0 the key for "undefined";
            indices greater than 5 are reserved for custom types. types_keep = (0,1,2,3,4) should handle most files.
        goal_num_pts (integer): number of points to sample
        min_step_change (float): stops while loop from infinitely trying closer and closer step sizes
        max_iters (integer): maximum number of iterations of while loop
        verbose (boolean): if true, will print step size information for each search iteration

    Returns:
        sampled_pts: list of xyz coordinates of sampled points
        num_pts: actual number of points sampled
        step_size: step size that samples required number of points
        i: number of iterations to reach viable step size
    """
    num_pts = 0
    min_step_size = 0.0
    max_step_size = total_length
    prev_step_size = max_step_size
    step_size = (min_step_size + max_step_size) / 2.0
    i = 0
    while num_pts != goal_num_pts and abs(step_size - prev_step_size) > min_step_change and i < \
            max_iters:
        i += 1
        sampled_pts_list, num_roots = sample_pts_step(vertices, vertex_coords, step_size, types_keep)
        if num_roots > goal_num_pts:
            warnings.warn("More connected components in neuron than points to sample, skipping")
            return None

        # continue binary search
        num_pts = len(sampled_pts_list)
        if num_pts < goal_num_pts:
            max_step_size = step_size
            prev_step_size = step_size
            step_size = (min_step_size + max_step_size) / 2.0
        elif num_pts > goal_num_pts:
            min_step_size = step_size
            prev_step_size = step_size
            step_size = (min_step_size + max_step_size) / 2.0
        # else will stop next loop

        if verbose:
            print("Iteration", i)
            print("Num pts", num_pts)
            print("Prev step size", prev_step_size)
            print("Step size", step_size)
            print("")
    if i == 0:
        raise Exception("Sampled 0 points from neuron, could be too large of min_step_change, or types_keep does not include values in second column of SWC files")
    else:
        sampled_pts = np.array(sampled_pts_list)
        return sampled_pts, num_pts, step_size, i


def sample_network_step(vertices : List[List[str]], vertex_coords : Dict[int,np.ndarray],
                                        step_size : float, types_keep : Optional[Iterable[int]] =None):
    """
    Sample points at every set interval (step_size) along branches of neuron, return networkx

    Args:
        vertices (list): list of rows from SWC file that are connected to the soma
        vertex_coords (dict): dictionary of xyz coordinates for the ID of each vertex in vertices_keep
        step_size (float): even distance to sample points radially from soma
        types_keep (tuple,list): list of SWC neuron part types to sample points from
            by default, uses only 1 (soma), 2 (axon), 3 (basal dendrite), 4 (apical dendrite)

    Returns:
        graph: networkx graph of sampled points weighted by distance between points
    """
    vertex_dist : Dict[int,float] = {}
    num_roots= 0
    graph = nx.Graph()
    prev_pts : Dict[int,str] = {}  # Save last point before this one so can connect edge
    # pos = {}

    types_keep_strings : Optional[List[str]]= None
    # in case types_keep are numbers
    if types_keep is not None:
        types_keep_strings = [str(x) for x in types_keep] if isinstance(types_keep, Iterable) else [str(types_keep)]

    # loop through list of vertices, sampling points from edge of vertex to parent
    for v in vertices:
        this_id = int(v[0])
        this_coord = np.array((float(v[2]), float(v[3]), float(v[4])))
        pid = int(v[-1])
        if pid < 0:
            num_roots += 1
            vertex_dist[this_id] = 0
            graph.add_node(str(this_id))
            # pos[str(this_id)] = this_coord[:2]
            prev_pts[this_id] = str(this_id)
            continue
        seg_len = euclidean(vertex_coords[pid], this_coord)
        pts_dist = np.arange(step_size, seg_len + vertex_dist[pid], step_size)
        if (types_keep_strings is None or v[1] in types_keep_strings) and len(pts_dist) > 0:
            pts_dist = pts_dist - vertex_dist[pid]
            new_dist = seg_len - pts_dist[-1]
            new_pts = [vertex_coords[pid] + (this_coord - vertex_coords[pid]) * x / seg_len for x in pts_dist]
            new_pts_ids = [prev_pts[pid]] + [str(this_id) + "_" + str(x) for x in range(len(pts_dist))]
            new_pts_len = [vertex_dist[pid] + euclidean(new_pts[0], vertex_coords[pid])] + \
                          [euclidean(new_pts[i], new_pts[i - 1]) for i in range(1, len(new_pts))]
            # Add new points to graph, with edge weighted by euclidean to parent
            if types_keep_strings is None or v[1] in types_keep_strings:
                for i in range(1, len(new_pts_ids)):
                    graph.add_node(new_pts_ids[i])
                    # pos[new_pts_ids[i]] = new_pts[i - 1][:2]
                    graph.add_edge(new_pts_ids[i - 1], new_pts_ids[i], weight=new_pts_len[i - 1])
            vertex_dist[this_id] = new_dist
            prev_pts[this_id] = new_pts_ids[-1]
        else:
            vertex_dist[this_id] = vertex_dist[pid] + seg_len
            prev_pts[this_id] = prev_pts[pid]
    return graph  # , pos


def get_sample_pts(file_name : str, infolder : str,
                   types_keep : Optional[Iterable[int]] =None,
                   goal_num_pts : int =50, min_step_change : float =1e-7,
                   max_iters : int =50, keep_disconnect : bool = True,
                   verbose: bool =False) -> Optional[Tuple[np.ndarray,int,float,int]]:
    """
    Sample points from SWC file

    Args:
        file_name (string): SWC file name (including .swc)
    
        infolder (string): path to folder containing SWC file
    
        types_keep (tuple,list): list of SWC neuron part types to sample points from. If types_keep is None then all part types are sampled.
    
        goal_num_pts (integer): number of points to sample.
    
        min_step_change (float): stops while loop from infinitely trying closer and closer step sizes
    
        max_iters (integer): maximum number of iterations of while loop
    
        keep_disconnect (boolean): if True, will keep all branches from SWC. If False, will keep only connected to soma
    
        verbose (boolean): if True, will print step size information for each search iteration

    Returns:
        None, if either of these occur:
    
        - The file does not end with ".swc" or ".SWC".
    
        - There are more connected components in the sample than goal_num_pts.

        Otherwise, a 4-tuple:

        [0]: list of xyz coordinates of sampled points
    
        [1]: actual number of points sampled
    
        [2]: step size that samples required number of points
    
        [3]: number of iterations to reach viable step size
    """

    if file_name[-4:] != ".SWC" and file_name[-4:] != ".swc":
        warnings.warn("Input file must be a .swc or .SWC file, skipping")
        return None

    # Read SWC file
    swc_list = read_swc(pj(infolder, file_name))

    # Get total length of segment type (for max step size)
    coord_list_out = prep_coord_dict(swc_list, types_keep,
                                     keep_disconnect=keep_disconnect)
    return sample_n_pts(coord_list_out[0], coord_list_out[1],
                        coord_list_out[2],
                        types_keep, goal_num_pts, min_step_change,
                        max_iters, verbose)


def compute_and_save_sample_pts(file_name: str, infolder : str, outfolder : str,
                    types_keep : Optional[Iterable[int]] = None,
                    goal_num_pts : int = 50, min_step_change : float =1e-7,
                    max_iters : int =50, keep_disconnect:bool=True,
                    verbose:bool=False) -> bool:
    """A wrapper function for get_sample_pts which saves the output as a
        comma-separated-value text file.  The output filename is the same as
        the input filename except that it ends in .csv instead of .swc.  The
        output text file will contain goal_num_pts rows and three
        comma-separated columns with the xyz values of the sampled points.  xyz
        coordinates are specified to 16 places after the decimal.
        

        Args:
    
            file_name (string): SWC file name (including .swc)
    
            infolder (string): path to folder containing SWC file
    
            outfolder (string): path to output folder to save CSVs
    
            types_keep (tuple,list): list of SWC neuron part types to sample points from. If types_keep is None, all points are sampled.

            goal_num_pts (integer): number of points to sample
    
            min_step_change (float): stops while loop from infinitely trying closer and closer step sizes
    
            max_iters (integer): maximum number of iterations of while loop
    
            keep_disconnect (boolean): if True, will keep all branches from SWC. if False, will keep only those connected to soma
    
            verbose (boolean): if true, will print step size information for each search iteration

        Returns:
            Boolean success of sampling points from this SWC file.

    """

    sample_pts_out = get_sample_pts(file_name, infolder, types_keep, goal_num_pts,
                                    min_step_change, max_iters, keep_disconnect, verbose)

    if sample_pts_out is None:
        return False

    if sample_pts_out[1] == goal_num_pts:
        np.savetxt(pj(outfolder, file_name[:-4] + ".csv"), np.array(sample_pts_out[0]), delimiter=",", fmt="%.16f")
        return True
    else:
        return False


def get_geodesic(file_name:str, infolder:str, types_keep:Optional[Iterable[int]]=None,
                 goal_num_pts : int =50, min_step_change : float =1e-7,
                 max_iters : int =50, verbose: bool=False) -> Optional[np.ndarray]:
    """
    Sample points from a given SWC file, compute the geodesic distance (networkx graph distance) between
    points, and return the matrix of pairwise geodesic distances between points in the cell.

    Args:
        file_name (string): SWC file name (including .swc)

        infolder (string): path to folder containing SWC file

        types_keep (tuple,list): list of SWC neuron part types to sample points from. By default, all points are kept. 

        goal_num_pts (integer): number of points to sample.

        min_step_change (float): stops while loop from infinitely trying closer and closer step sizes

        max_iters (integer): maximum number of iterations of while loop

        verbose (boolean): if true, will print step size information for each search iteration

    Returns:

        None, if either of these occur:
    
        - The file does not end with ".swc" or ".SWC".
    
        - There are more connected components in the sample than goal_num_pts.

        Otherwise, returns a numpy vector-form distance vector encoding the intracell geodesic distance matrix 
       
    """

    if file_name[-4:] != ".SWC" and file_name[-4:] != ".swc":
        warnings.warn("Input file must be a .swc or .SWC file, skipping")
        return None

    # Read SWC file
    swc_list = read_swc(pj(infolder, file_name))

    # Get total length of segment type (for max step size)
    coord_list_out = prep_coord_dict(swc_list, types_keep, keep_disconnect=False)

    sample_pts_out = sample_n_pts(coord_list_out[0], coord_list_out[1], coord_list_out[2], types_keep,
                                  goal_num_pts, min_step_change, max_iters, verbose)
    if sample_pts_out is None:
        return None

    if sample_pts_out[1] == goal_num_pts:
        # sample_network, pos = sample_network_step(coord_list_out[0], coord_list_out[1], sample_pts_out[2], types_keep)
        sample_network = sample_network_step(coord_list_out[0], coord_list_out[1], sample_pts_out[2], types_keep)
        geo_dist_mat = squareform(nx.algorithms.shortest_paths.dense.floyd_warshall_numpy(sample_network))
        return geo_dist_mat
    else:
        return None


def compute_and_save_geodesic(file_name : str, infolder:str, outfolder:str,
                  types_keep : Optional[Iterable[int]] =None,
                  goal_num_pts : int =50, min_step_change : float =1e-7,
                  max_iters: int =50, verbose : bool =False) -> bool:
    """
    A wrapper for get_geodesic which writes the results to a text file. If the input filename is "file_name.swc" then the output filename will be "file_name_dist.txt".

    The file has a single column. The rows of the file are the distances d(x_i,x_j) for x_i, x_j sample points and i < j.

    The distances are floating point real numbers specified to 8 places past the decimal.
    

    Args:
        file_name (string): SWC file name (including .swc)
    
        infolder (string): path to folder containing SWC file

        outfolder (string): path to output folder to save distance vectors

        types_keep (tuple,list): list of SWC neuron part types to sample points from. By default, uses all.
    
        goal_num_pts (integer): number of points to sample
    
        min_step_change (float): stops while loop from infinitely trying closer and closer step sizes
    
        max_iters (integer): maximum number of iterations of while loop
    
        verbose (boolean): if true, will print step size information for each search iteration

    Returns:
        Boolean success of sampling points from this SWC file.
    """
    geo_dist_mat = get_geodesic(file_name, infolder, types_keep, goal_num_pts, min_step_change, max_iters, verbose)

    if geo_dist_mat is not None:
        np.savetxt(pj(outfolder, file_name[:-4] + "_dist.txt"), geo_dist_mat, fmt='%.8f')
        return True
    else:
        return False


def compute_and_save_sample_pts_parallel(infolder : str, outfolder : str,
                             types_keep: Optional[Iterable[int]]=None,
                             goal_num_pts : int =50, min_step_change :float =1e-7,
                             max_iters : int =50, num_cores :int =8,
                             keep_disconnect: bool =True) -> Iterable[bool]:
    """
    Parallelize sampling the same number of points from all SWC files in a folder.

    Args:
    
        infolder (string): path to folder containing SWC files. Only files ending in '.SWC' or '.swc' will be processed, other files will be ignored with a warning
    
        outfolder (string): path to output folder to save .csv files.
    
        types_keep (tuple,list): list of SWC neuron part types to sample points from.
     
        goal_num_pts (integer): number of points to sample
    
        min_step_change (float): stops while loop from infinitely trying closer and closer step sizes
    
        max_iters (integer): maximum number of iterations of while loop
    
        num_cores (integer): number of processes to use for parallelization
    
        keep_disconnect (boolean): if True, will keep all branches from SWC. if False, will keep only connected to soma

    Returns:
        A lazy list of Booleans which describe the success or failure of each file.
    """
    
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    arguments = [(file_name, infolder, outfolder, types_keep, goal_num_pts,
                  min_step_change, max_iters, keep_disconnect, False)
                 for file_name in os.listdir(infolder)]
    # start = time.time()
    with Pool(processes=num_cores) as pool:
        return(pool.starmap(compute_and_save_sample_pts, arguments))
    # print(time.time() - start)


def compute_and_save_geodesic_parallel(infolder : str,
                    outfolder : str, types_keep : Optional[Iterable[int]]=None,
                    goal_num_pts : int =50, min_step_change : float =1e-7,
                    max_iters : int =50, num_cores: int =8) -> Iterable[bool]:
    """
    Parallelize sampling and computing geodesic distance for the same number of points from all SWC files in a folder

    Args:
        infolder (string): path to folder containing SWC files
    
        outfolder (string): path to output folder to save distance vectors
    
        types_keep (tuple,list): list of SWC neuron part types to sample points from. By default, all parts will be used.

        goal_num_pts (integer): number of points to sample
    
        min_step_change (float): stops while loop from infinitely trying closer and closer step sizes
    
        max_iters (integer): maximum number of iterations of while loop
    
        num_cores (integer): number of processes to use for parallelization

    Returns:
        A lazy list of Booleans indicating the success or failure for each file in the folder
    """
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    arguments = [(file_name, infolder, outfolder, types_keep, goal_num_pts, min_step_change, max_iters, False)
                 for file_name in os.listdir(infolder)]
    # start = time.time()
    with Pool(processes=num_cores) as pool:
        return(pool.starmap(compute_and_save_geodesic, arguments))
    # print(time.time() - start)

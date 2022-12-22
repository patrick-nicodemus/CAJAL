from .core import *
from _typeshed import Incomplete

class PointCloudHeatSolver:
    bound_solver: Incomplete
    def __init__(self, P, t_coef: float = ...) -> None: ...
    def compute_distance(self, p_ind): ...
    def compute_distance_multisource(self, p_inds): ...
    def extend_scalar(self, p_inds, values): ...
    def get_tangent_frames(self): ...
    def transport_tangent_vector(self, p_ind, vector): ...
    def transport_tangent_vectors(self, p_inds, vectors): ...
    def compute_log_map(self, p_ind): ...

class PointCloudLocalTriangulation:
    bound_triangulation: Incomplete
    def __init__(self, P, with_degeneracy_heuristic: bool = ...) -> None: ...
    def get_local_triangulation(self): ...
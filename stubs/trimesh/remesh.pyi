from . import grouping as grouping, util as util
from .geometry import faces_to_edges as faces_to_edges
from _typeshed import Incomplete

def subdivide(vertices, faces, face_index: Incomplete | None = ..., vertex_attributes: Incomplete | None = ..., return_index: bool = ...): ...
def subdivide_to_size(vertices, faces, max_edge, max_iter: int = ..., return_index: bool = ...): ...
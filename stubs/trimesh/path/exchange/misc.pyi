from ... import graph as graph, grouping as grouping, util as util
from ..entities import Arc as Arc, Line as Line
from _typeshed import Incomplete

def dict_to_path(as_dict): ...
def lines_to_path(lines): ...
def polygon_to_path(polygon): ...
def linestrings_to_path(multi): ...
def faces_to_path(mesh, face_ids: Incomplete | None = ..., **kwargs): ...
def edges_to_path(edges, vertices, **kwargs): ...
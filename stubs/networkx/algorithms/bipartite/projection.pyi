from _typeshed import Incomplete

def projected_graph(B, nodes, multigraph: bool = ...): ...
def weighted_projected_graph(B, nodes, ratio: bool = ...): ...
def collaboration_weighted_projected_graph(B, nodes): ...
def overlap_weighted_projected_graph(B, nodes, jaccard: bool = ...): ...
def generic_weighted_projected_graph(B, nodes, weight_function: Incomplete | None = ...): ...
def project(B, nodes, create_using: Incomplete | None = ...): ...
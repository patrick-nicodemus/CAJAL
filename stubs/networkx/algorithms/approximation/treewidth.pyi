from _typeshed import Incomplete

def treewidth_min_degree(G): ...
def treewidth_min_fill_in(G): ...

class MinDegreeHeuristic:
    count: Incomplete
    def __init__(self, graph) -> None: ...
    def best_node(self, graph): ...
from _typeshed import Incomplete
from networkx.utils import pairwise as pairwise

def validate_path(G, s, t, soln_len, path, weight: str = ...): ...
def validate_length_path(G, s, t, soln_len, length, path, weight: str = ...) -> None: ...

class WeightedTestBase:
    grid: Incomplete
    cycle: Incomplete
    directed_cycle: Incomplete
    XG: Incomplete
    MXG: Incomplete
    XG2: Incomplete
    XG3: Incomplete
    XG4: Incomplete
    MXG4: Incomplete
    G: Incomplete
    def setup(self) -> None: ...

class TestWeightedPath(WeightedTestBase):
    def test_dijkstra(self) -> None: ...
    def test_bidirectional_dijkstra(self) -> None: ...
    def test_weight_functions(self): ...
    def test_bidirectional_dijkstra_no_path(self) -> None: ...
    def test_absent_source(self, fn) -> None: ...
    def test_dijkstra_predecessor1(self) -> None: ...
    def test_dijkstra_predecessor2(self) -> None: ...
    def test_dijkstra_predecessor3(self) -> None: ...
    def test_single_source_dijkstra_path_length(self) -> None: ...
    def test_bidirectional_dijkstra_multigraph(self) -> None: ...
    def test_dijkstra_pred_distance_multigraph(self) -> None: ...
    def test_negative_edge_cycle(self) -> None: ...
    def test_negative_edge_cycle_custom_weight_key(self) -> None: ...
    def test_weight_function(self): ...
    def test_all_pairs_dijkstra_path(self) -> None: ...
    def test_all_pairs_dijkstra_path_length(self) -> None: ...
    def test_all_pairs_dijkstra(self) -> None: ...

class TestDijkstraPathLength:
    def test_weight_function(self): ...

class TestMultiSourceDijkstra:
    def test_no_sources(self) -> None: ...
    def test_path_no_sources(self) -> None: ...
    def test_path_length_no_sources(self) -> None: ...
    def test_absent_source(self, fn) -> None: ...
    def test_two_sources(self) -> None: ...
    def test_simple_paths(self) -> None: ...

class TestBellmanFordAndGoldbergRadzik(WeightedTestBase):
    def test_single_node_graph(self) -> None: ...
    def test_absent_source_bellman_ford(self) -> None: ...
    def test_absent_source_goldberg_radzik(self) -> None: ...
    def test_negative_cycle_heuristic(self) -> None: ...
    def test_negative_cycle_consistency(self) -> None: ...
    def test_negative_cycle(self) -> None: ...
    def test_find_negative_cycle_longer_cycle(self) -> None: ...
    def test_find_negative_cycle_no_cycle(self) -> None: ...
    def test_find_negative_cycle_single_edge(self) -> None: ...
    def test_negative_weight(self) -> None: ...
    def test_not_connected(self) -> None: ...
    def test_multigraph(self) -> None: ...
    def test_others(self) -> None: ...
    def test_path_graph(self) -> None: ...
    def test_4_cycle(self) -> None: ...
    def test_negative_weight_bf_path(self) -> None: ...
    def test_zero_cycle_smoke(self) -> None: ...

class TestJohnsonAlgorithm(WeightedTestBase):
    def test_single_node_graph(self) -> None: ...
    def test_negative_cycle(self) -> None: ...
    def test_negative_weights(self) -> None: ...
    def test_unweighted_graph(self) -> None: ...
    def test_graphs(self) -> None: ...

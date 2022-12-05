from _typeshed import Incomplete
from networkx.algorithms.bipartite.matching import eppstein_matching as eppstein_matching, hopcroft_karp_matching as hopcroft_karp_matching, maximum_matching as maximum_matching, minimum_weight_full_matching as minimum_weight_full_matching, to_vertex_cover as to_vertex_cover

class TestMatching:
    simple_graph: Incomplete
    simple_solution: Incomplete
    top_nodes: Incomplete
    graph: Incomplete
    disconnected_graph: Incomplete
    def setup(self) -> None: ...
    def check_match(self, matching) -> None: ...
    def check_vertex_cover(self, vertices) -> None: ...
    def test_eppstein_matching(self) -> None: ...
    def test_hopcroft_karp_matching(self) -> None: ...
    def test_to_vertex_cover(self) -> None: ...
    def test_eppstein_matching_simple(self) -> None: ...
    def test_hopcroft_karp_matching_simple(self) -> None: ...
    def test_eppstein_matching_disconnected(self) -> None: ...
    def test_hopcroft_karp_matching_disconnected(self) -> None: ...
    def test_issue_2127(self) -> None: ...
    def test_vertex_cover_issue_2384(self) -> None: ...
    def test_vertex_cover_issue_3306(self) -> None: ...
    def test_unorderable_nodes(self) -> None: ...

def test_eppstein_matching() -> None: ...

class TestMinimumWeightFullMatching:
    @classmethod
    def setup_class(cls) -> None: ...
    def test_minimum_weight_full_matching_incomplete_graph(self) -> None: ...
    def test_minimum_weight_full_matching_with_no_full_matching(self) -> None: ...
    def test_minimum_weight_full_matching_square(self) -> None: ...
    def test_minimum_weight_full_matching_smaller_left(self) -> None: ...
    def test_minimum_weight_full_matching_smaller_top_nodes_right(self) -> None: ...
    def test_minimum_weight_full_matching_smaller_right(self) -> None: ...
    def test_minimum_weight_full_matching_negative_weights(self) -> None: ...
    def test_minimum_weight_full_matching_different_weight_key(self) -> None: ...

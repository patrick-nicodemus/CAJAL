from networkx.algorithms import bipartite as bipartite

class TestBipartiteBasic:
    def test_is_bipartite(self) -> None: ...
    def test_bipartite_color(self) -> None: ...
    def test_not_bipartite_color(self) -> None: ...
    def test_bipartite_directed(self) -> None: ...
    def test_bipartite_sets(self) -> None: ...
    def test_bipartite_sets_directed(self) -> None: ...
    def test_bipartite_sets_given_top_nodes(self) -> None: ...
    def test_bipartite_sets_disconnected(self) -> None: ...
    def test_is_bipartite_node_set(self) -> None: ...
    def test_bipartite_density(self) -> None: ...
    def test_bipartite_degrees(self) -> None: ...
    def test_bipartite_weighted_degrees(self) -> None: ...
    def test_biadjacency_matrix_weight(self) -> None: ...
    def test_biadjacency_matrix(self) -> None: ...
    def test_biadjacency_matrix_order(self) -> None: ...

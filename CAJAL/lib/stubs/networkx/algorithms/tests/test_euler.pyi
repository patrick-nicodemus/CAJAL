class TestIsEulerian:
    def test_is_eulerian(self) -> None: ...
    def test_is_eulerian2(self) -> None: ...

class TestEulerianCircuit:
    def test_eulerian_circuit_cycle(self) -> None: ...
    def test_eulerian_circuit_digraph(self) -> None: ...
    def test_multigraph(self) -> None: ...
    def test_multigraph_with_keys(self) -> None: ...
    def test_not_eulerian(self) -> None: ...

class TestIsSemiEulerian:
    def test_is_semieulerian(self) -> None: ...

class TestHasEulerianPath:
    def test_has_eulerian_path_cyclic(self) -> None: ...
    def test_has_eulerian_path_non_cyclic(self) -> None: ...
    def test_has_eulerian_path_directed_graph(self) -> None: ...
    def test_has_eulerian_path_not_weakly_connected(self, G) -> None: ...
    def test_has_eulerian_path_unbalancedins_more_than_one(self, G) -> None: ...

class TestFindPathStart:
    def testfind_path_start(self) -> None: ...

class TestEulerianPath:
    def test_eulerian_path(self) -> None: ...
    def test_eulerian_path_straight_link(self) -> None: ...
    def test_eulerian_path_multigraph(self) -> None: ...
    def test_eulerian_path_eulerian_circuit(self) -> None: ...
    def test_eulerian_path_undirected(self) -> None: ...
    def test_eulerian_path_multigraph_undirected(self) -> None: ...

class TestEulerize:
    def test_disconnected(self) -> None: ...
    def test_null_graph(self) -> None: ...
    def test_null_multigraph(self) -> None: ...
    def test_on_empty_graph(self) -> None: ...
    def test_on_eulerian(self) -> None: ...
    def test_on_eulerian_multigraph(self) -> None: ...
    def test_on_complete_graph(self) -> None: ...

class TestCutSize:
    def test_symmetric(self) -> None: ...
    def test_single_edge(self) -> None: ...
    def test_directed(self) -> None: ...
    def test_directed_symmetric(self) -> None: ...
    def test_multigraph(self) -> None: ...

class TestVolume:
    def test_graph(self) -> None: ...
    def test_digraph(self) -> None: ...
    def test_multigraph(self) -> None: ...
    def test_multidigraph(self) -> None: ...
    def test_barbell(self) -> None: ...

class TestNormalizedCutSize:
    def test_graph(self) -> None: ...
    def test_directed(self) -> None: ...

class TestConductance:
    def test_graph(self) -> None: ...

class TestEdgeExpansion:
    def test_graph(self) -> None: ...

class TestNodeExpansion:
    def test_graph(self) -> None: ...

class TestBoundaryExpansion:
    def test_graph(self) -> None: ...

class TestMixingExpansion:
    def test_graph(self) -> None: ...

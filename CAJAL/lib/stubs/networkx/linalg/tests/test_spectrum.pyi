from _typeshed import Incomplete
from networkx.generators.degree_seq import havel_hakimi_graph as havel_hakimi_graph

np: Incomplete

class TestSpectrum:
    @classmethod
    def setup_class(cls) -> None: ...
    def test_laplacian_spectrum(self) -> None: ...
    def test_normalized_laplacian_spectrum(self) -> None: ...
    def test_adjacency_spectrum(self) -> None: ...
    def test_modularity_spectrum(self) -> None: ...
    def test_bethe_hessian_spectrum(self) -> None: ...

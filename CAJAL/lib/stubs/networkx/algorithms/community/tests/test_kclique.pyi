from _typeshed import Incomplete
from networkx.algorithms.community import k_clique_communities as k_clique_communities

def test_overlapping_K5() -> None: ...
def test_isolated_K5() -> None: ...

class TestZacharyKarateClub:
    G: Incomplete
    def setup(self) -> None: ...
    def test_k2(self) -> None: ...
    def test_k3(self) -> None: ...
    def test_k4(self) -> None: ...
    def test_k5(self) -> None: ...
    def test_k6(self) -> None: ...

def test_bad_k() -> None: ...

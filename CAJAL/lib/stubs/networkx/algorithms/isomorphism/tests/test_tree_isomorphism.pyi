from networkx.algorithms.isomorphism.tree_isomorphism import rooted_tree_isomorphism as rooted_tree_isomorphism, tree_isomorphism as tree_isomorphism
from networkx.classes.function import is_directed as is_directed

def check_isomorphism(t1, t2, isomorphism): ...
def test_hardcoded() -> None: ...
def random_swap(t): ...
def positive_single_tree(t1) -> None: ...
def test_positive(maxk: int = ...) -> None: ...
def test_trivial() -> None: ...
def test_trivial_2() -> None: ...
def test_negative(maxk: int = ...) -> None: ...

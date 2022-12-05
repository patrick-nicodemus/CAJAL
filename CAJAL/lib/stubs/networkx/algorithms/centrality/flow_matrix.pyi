from _typeshed import Incomplete
from collections.abc import Generator

def flow_matrix_row(G, weight: Incomplete | None = ..., dtype=..., solver: str = ...) -> Generator[Incomplete, None, None]: ...

class InverseLaplacian:
    dtype: Incomplete
    n: Incomplete
    w: Incomplete
    C: Incomplete
    L1: Incomplete
    def __init__(self, L, width: Incomplete | None = ..., dtype: Incomplete | None = ...) -> None: ...
    def init_solver(self, L) -> None: ...
    def solve(self, r) -> None: ...
    def solve_inverse(self, r) -> None: ...
    def get_rows(self, r1, r2): ...
    def get_row(self, r): ...
    def width(self, L): ...

class FullInverseLaplacian(InverseLaplacian):
    IL: Incomplete
    def init_solver(self, L) -> None: ...
    def solve(self, rhs): ...
    def solve_inverse(self, r): ...

class SuperLUInverseLaplacian(InverseLaplacian):
    lusolve: Incomplete
    def init_solver(self, L) -> None: ...
    def solve_inverse(self, r): ...
    def solve(self, rhs): ...

class CGInverseLaplacian(InverseLaplacian):
    M: Incomplete
    def init_solver(self, L) -> None: ...
    def solve(self, rhs): ...
    def solve_inverse(self, r): ...

from _typeshed import Incomplete
from collections.abc import Generator

def is_eulerian(G): ...
def is_semieulerian(G): ...
def eulerian_circuit(G, source: Incomplete | None = ..., keys: bool = ...) -> Generator[Incomplete, None, None]: ...
def has_eulerian_path(G, source: Incomplete | None = ...): ...
def eulerian_path(G, source: Incomplete | None = ..., keys: bool = ...) -> Generator[Incomplete, None, None]: ...
def eulerize(G): ...

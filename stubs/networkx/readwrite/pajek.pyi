from _typeshed import Incomplete
from collections.abc import Generator

def generate_pajek(G) -> Generator[Incomplete, None, None]: ...
def write_pajek(G, path, encoding: str = ...) -> None: ...
def read_pajek(path, encoding: str = ...): ...
def parse_pajek(lines): ...
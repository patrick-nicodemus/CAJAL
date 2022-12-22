from _typeshed import Incomplete

class _HeapElement:
    priority: Incomplete
    element: Incomplete
    def __init__(self, priority, element) -> None: ...
    def __lt__(self, other): ...
    def __gt__(self, other): ...
    def __eq__(self, other): ...
    def __hash__(self): ...
    def __getitem__(self, indx): ...
    def __iter__(self): ...

class MappedQueue:
    heap: Incomplete
    position: Incomplete
    def __init__(self, data=...) -> None: ...
    def __len__(self) -> int: ...
    def push(self, elt, priority: Incomplete | None = ...): ...
    def pop(self): ...
    def update(self, elt, new, priority: Incomplete | None = ...) -> None: ...
    def remove(self, elt) -> None: ...
from _typeshed import Incomplete

class DupFd:
    def __init__(self, fd) -> None: ...
    def detach(self): ...

class _ResourceSharer:
    def __init__(self) -> None: ...
    def register(self, send, close): ...
    @staticmethod
    def get_connection(ident): ...
    def stop(self, timeout: Incomplete | None = ...) -> None: ...

stop: Incomplete
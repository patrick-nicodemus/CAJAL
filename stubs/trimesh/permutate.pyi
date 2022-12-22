from . import transformations as transformations, util as util
from _typeshed import Incomplete

def transform(mesh, translation_scale: float = ...): ...
def noise(mesh, magnitude: Incomplete | None = ...): ...
def tessellation(mesh): ...

class Permutator:
    def __init__(self, mesh) -> None: ...
    def transform(self, translation_scale: int = ...): ...
    def noise(self, magnitude: Incomplete | None = ...): ...
    def tessellation(self): ...
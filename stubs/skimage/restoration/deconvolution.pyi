from . import uft as uft
from .._shared.utils import deprecate_kwarg as deprecate_kwarg
from _typeshed import Incomplete

def wiener(image, psf, balance, reg: Incomplete | None = ..., is_real: bool = ..., clip: bool = ...): ...
def unsupervised_wiener(image, psf, reg: Incomplete | None = ..., user_params: Incomplete | None = ..., is_real: bool = ..., clip: bool = ..., *, random_state: Incomplete | None = ...): ...
def richardson_lucy(image, psf, num_iter: int = ..., clip: bool = ..., filter_epsilon: Incomplete | None = ...): ...
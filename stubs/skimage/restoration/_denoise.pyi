from .. import color as color
from .._shared import utils as utils
from .._shared.utils import warn as warn
from ..color.colorconv import ycbcr_from_rgb as ycbcr_from_rgb
from ..util.dtype import img_as_float as img_as_float
from _typeshed import Incomplete

def denoise_bilateral(image, win_size: Incomplete | None = ..., sigma_color: Incomplete | None = ..., sigma_spatial: int = ..., bins: int = ..., mode: str = ..., cval: int = ..., multichannel: bool = ..., *, channel_axis: Incomplete | None = ...): ...
def denoise_tv_bregman(image, weight: float = ..., max_num_iter: int = ..., eps: float = ..., isotropic: bool = ..., *, channel_axis: Incomplete | None = ..., multichannel: bool = ...): ...
def denoise_tv_chambolle(image, weight: float = ..., eps: float = ..., max_num_iter: int = ..., multichannel: bool = ..., *, channel_axis: Incomplete | None = ...): ...
def denoise_wavelet(image, sigma: Incomplete | None = ..., wavelet: str = ..., mode: str = ..., wavelet_levels: Incomplete | None = ..., multichannel: bool = ..., convert2ycbcr: bool = ..., method: str = ..., rescale_sigma: bool = ..., *, channel_axis: Incomplete | None = ...): ...
def estimate_sigma(image, average_sigmas: bool = ..., multichannel: bool = ..., *, channel_axis: Incomplete | None = ...): ...
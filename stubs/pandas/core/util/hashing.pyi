import numpy as np
from pandas import Categorical as Categorical, DataFrame as DataFrame, Index as Index, MultiIndex as MultiIndex, Series as Series
from pandas._libs import lib as lib
from pandas._libs.hashing import hash_object_array as hash_object_array
from pandas._typing import ArrayLike as ArrayLike, npt as npt
from pandas.core.dtypes.common import is_categorical_dtype as is_categorical_dtype, is_list_like as is_list_like
from pandas.core.dtypes.generic import ABCDataFrame as ABCDataFrame, ABCExtensionArray as ABCExtensionArray, ABCIndex as ABCIndex, ABCMultiIndex as ABCMultiIndex, ABCSeries as ABCSeries
from typing import Hashable, Iterable, Iterator

def combine_hash_arrays(arrays: Iterator[np.ndarray], num_items: int) -> npt.NDArray[np.uint64]: ...
def hash_pandas_object(obj: Union[Index, DataFrame, Series], index: bool = ..., encoding: str = ..., hash_key: Union[str, None] = ..., categorize: bool = ...) -> Series: ...
def hash_tuples(vals: Union[MultiIndex, Iterable[tuple[Hashable, ...]]], encoding: str = ..., hash_key: str = ...) -> npt.NDArray[np.uint64]: ...
def hash_array(vals: ArrayLike, encoding: str = ..., hash_key: str = ..., categorize: bool = ...) -> npt.NDArray[np.uint64]: ...
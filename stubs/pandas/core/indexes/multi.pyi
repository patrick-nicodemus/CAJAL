import numpy as np
from _typeshed import Incomplete
from pandas import CategoricalIndex as CategoricalIndex, DataFrame as DataFrame, Series as Series
from pandas._config import get_option as get_option
from pandas._libs import index as libindex, lib as lib
from pandas._libs.hashtable import duplicated as duplicated
from pandas._typing import AnyArrayLike as AnyArrayLike, DtypeObj as DtypeObj, F as F, Scalar as Scalar, Shape as Shape, npt as npt
from pandas.core.arrays import Categorical as Categorical
from pandas.core.arrays.categorical import factorize_from_iterables as factorize_from_iterables
from pandas.core.dtypes.cast import coerce_indexer_dtype as coerce_indexer_dtype
from pandas.core.dtypes.common import ensure_int64 as ensure_int64, ensure_platform_int as ensure_platform_int, is_categorical_dtype as is_categorical_dtype, is_extension_array_dtype as is_extension_array_dtype, is_hashable as is_hashable, is_integer as is_integer, is_iterator as is_iterator, is_list_like as is_list_like, is_object_dtype as is_object_dtype, is_scalar as is_scalar, pandas_dtype as pandas_dtype
from pandas.core.dtypes.dtypes import ExtensionDtype as ExtensionDtype
from pandas.core.dtypes.generic import ABCDataFrame as ABCDataFrame, ABCDatetimeIndex as ABCDatetimeIndex, ABCTimedeltaIndex as ABCTimedeltaIndex
from pandas.core.dtypes.missing import array_equivalent as array_equivalent, isna as isna
from pandas.core.indexes.base import Index as Index, ensure_index as ensure_index, get_unanimous_names as get_unanimous_names
from pandas.core.indexes.frozen import FrozenList as FrozenList
from pandas.core.ops.invalid import make_invalid_op as make_invalid_op
from pandas.core.sorting import get_group_index as get_group_index, indexer_from_factorized as indexer_from_factorized, lexsort_indexer as lexsort_indexer
from pandas.errors import InvalidIndexError as InvalidIndexError, PerformanceWarning as PerformanceWarning, UnsortedIndexError as UnsortedIndexError
from pandas.io.formats.printing import pprint_thing as pprint_thing
from pandas.util._decorators import Appender as Appender, cache_readonly as cache_readonly, deprecate_nonkeyword_arguments as deprecate_nonkeyword_arguments, doc as doc
from pandas.util._exceptions import find_stack_level as find_stack_level
from typing import Any, Callable, Hashable, Iterable, Literal, Sequence

class MultiIndexUIntEngine(libindex.BaseMultiIndexCodesEngine, libindex.UInt64Engine): ...
class MultiIndexPyIntEngine(libindex.BaseMultiIndexCodesEngine, libindex.ObjectEngine): ...

def names_compat(meth: F) -> F: ...

class MultiIndex(Index):
    sortorder: Union[int, None]
    def __new__(cls, levels: Incomplete | None = ..., codes: Incomplete | None = ..., sortorder: Incomplete | None = ..., names: Incomplete | None = ..., dtype: Incomplete | None = ..., copy: bool = ..., name: Incomplete | None = ..., verify_integrity: bool = ...) -> MultiIndex: ...
    @classmethod
    def from_arrays(cls, arrays, sortorder: Incomplete | None = ..., names=...) -> MultiIndex: ...
    @classmethod
    def from_tuples(cls, tuples: Iterable[tuple[Hashable, ...]], sortorder: Union[int, None] = ..., names: Union[Sequence[Hashable], Hashable, None] = ...) -> MultiIndex: ...
    @classmethod
    def from_product(cls, iterables: Sequence[Iterable[Hashable]], sortorder: Union[int, None] = ..., names: Union[Sequence[Hashable], lib.NoDefault] = ...) -> MultiIndex: ...
    @classmethod
    def from_frame(cls, df: DataFrame, sortorder: Incomplete | None = ..., names: Incomplete | None = ...) -> MultiIndex: ...
    @property
    def values(self) -> np.ndarray: ...
    @property
    def array(self) -> None: ...
    def dtypes(self) -> Series: ...
    def __len__(self) -> int: ...
    def levels(self) -> FrozenList: ...
    def set_levels(self, levels, level: Incomplete | None = ..., inplace: Incomplete | None = ..., verify_integrity: bool = ...): ...
    @property
    def nlevels(self) -> int: ...
    @property
    def levshape(self) -> Shape: ...
    @property
    def codes(self): ...
    def set_codes(self, codes, level: Incomplete | None = ..., inplace: Incomplete | None = ..., verify_integrity: bool = ...): ...
    def copy(self, names: Incomplete | None = ..., dtype: Incomplete | None = ..., levels: Incomplete | None = ..., codes: Incomplete | None = ..., deep: bool = ..., name: Incomplete | None = ...): ...
    def __array__(self, dtype: Incomplete | None = ...) -> np.ndarray: ...
    def view(self, cls: Incomplete | None = ...): ...
    def __contains__(self, key: Any) -> bool: ...
    def dtype(self) -> np.dtype: ...
    def memory_usage(self, deep: bool = ...) -> int: ...
    def nbytes(self) -> int: ...
    def format(self, name: Union[bool, None] = ..., formatter: Union[Callable, None] = ..., na_rep: Union[str, None] = ..., names: bool = ..., space: int = ..., sparsify: Incomplete | None = ..., adjoin: bool = ...) -> list: ...
    names: Incomplete
    def inferred_type(self) -> str: ...
    def is_monotonic_increasing(self) -> bool: ...
    def is_monotonic_decreasing(self) -> bool: ...
    def duplicated(self, keep: str = ...) -> npt.NDArray[np.bool_]: ...
    def fillna(self, value: Incomplete | None = ..., downcast: Incomplete | None = ...) -> None: ...
    def dropna(self, how: str = ...) -> MultiIndex: ...
    def get_level_values(self, level): ...
    def unique(self, level: Incomplete | None = ...): ...
    def to_frame(self, index: bool = ..., name=..., allow_duplicates: bool = ...) -> DataFrame: ...
    def to_flat_index(self) -> Index: ...
    def is_lexsorted(self) -> bool: ...
    @property
    def lexsort_depth(self) -> int: ...
    def remove_unused_levels(self) -> MultiIndex: ...
    def __reduce__(self): ...
    def __getitem__(self, key): ...
    def take(self, indices, axis: int = ..., allow_fill: bool = ..., fill_value: Incomplete | None = ..., **kwargs) -> MultiIndex: ...
    def append(self, other): ...
    def argsort(self, *args, **kwargs) -> npt.NDArray[np.intp]: ...
    def repeat(self, repeats: int, axis: Incomplete | None = ...) -> MultiIndex: ...
    def drop(self, codes, level: Incomplete | None = ..., errors: str = ...): ...
    def swaplevel(self, i: int = ..., j: int = ...) -> MultiIndex: ...
    def reorder_levels(self, order) -> MultiIndex: ...
    def sortlevel(self, level: int = ..., ascending: bool = ..., sort_remaining: bool = ...) -> tuple[MultiIndex, npt.NDArray[np.intp]]: ...
    def get_slice_bound(self, label: Union[Hashable, Sequence[Hashable]], side: Literal['left', 'right'], kind=...) -> int: ...
    def slice_locs(self, start: Incomplete | None = ..., end: Incomplete | None = ..., step: Incomplete | None = ..., kind=...) -> tuple[int, int]: ...
    def get_loc(self, key, method: Incomplete | None = ...): ...
    def get_loc_level(self, key, level: int = ..., drop_level: bool = ...): ...
    def get_locs(self, seq): ...
    def truncate(self, before: Incomplete | None = ..., after: Incomplete | None = ...) -> MultiIndex: ...
    def equals(self, other: object) -> bool: ...
    def equal_levels(self, other: MultiIndex) -> bool: ...
    def astype(self, dtype, copy: bool = ...): ...
    def insert(self, loc: int, item) -> MultiIndex: ...
    def delete(self, loc) -> MultiIndex: ...
    def isin(self, values, level: Incomplete | None = ...) -> npt.NDArray[np.bool_]: ...
    def set_names(self, names, level: Incomplete | None = ..., inplace: bool = ...) -> Union[MultiIndex, None]: ...
    rename: Incomplete
    def drop_duplicates(self, keep: Union[str, bool] = ...) -> MultiIndex: ...
    __add__: Incomplete
    __radd__: Incomplete
    __iadd__: Incomplete
    __sub__: Incomplete
    __rsub__: Incomplete
    __isub__: Incomplete
    __pow__: Incomplete
    __rpow__: Incomplete
    __mul__: Incomplete
    __rmul__: Incomplete
    __floordiv__: Incomplete
    __rfloordiv__: Incomplete
    __truediv__: Incomplete
    __rtruediv__: Incomplete
    __mod__: Incomplete
    __rmod__: Incomplete
    __divmod__: Incomplete
    __rdivmod__: Incomplete
    __neg__: Incomplete
    __pos__: Incomplete
    __abs__: Incomplete
    __invert__: Incomplete

def sparsify_labels(label_list, start: int = ..., sentinel: str = ...): ...
def maybe_droplevels(index: Index, key) -> Index: ...
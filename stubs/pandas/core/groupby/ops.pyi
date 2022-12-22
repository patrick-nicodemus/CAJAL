import numpy as np
from _typeshed import Incomplete
from pandas._libs import NaT as NaT, lib as lib
from pandas._typing import ArrayLike as ArrayLike, DtypeObj as DtypeObj, NDFrameT as NDFrameT, Shape as Shape, npt as npt
from pandas.core.arrays import Categorical as Categorical, DatetimeArray as DatetimeArray, ExtensionArray as ExtensionArray, PeriodArray as PeriodArray, TimedeltaArray as TimedeltaArray
from pandas.core.arrays.boolean import BooleanDtype as BooleanDtype
from pandas.core.arrays.floating import FloatingDtype as FloatingDtype
from pandas.core.arrays.integer import IntegerDtype as IntegerDtype
from pandas.core.arrays.masked import BaseMaskedArray as BaseMaskedArray, BaseMaskedDtype as BaseMaskedDtype
from pandas.core.arrays.string_ import StringDtype as StringDtype
from pandas.core.dtypes.cast import maybe_cast_pointwise_result as maybe_cast_pointwise_result, maybe_downcast_to_dtype as maybe_downcast_to_dtype
from pandas.core.dtypes.common import ensure_float64 as ensure_float64, ensure_int64 as ensure_int64, ensure_platform_int as ensure_platform_int, ensure_uint64 as ensure_uint64, is_1d_only_ea_dtype as is_1d_only_ea_dtype, is_bool_dtype as is_bool_dtype, is_complex_dtype as is_complex_dtype, is_datetime64_any_dtype as is_datetime64_any_dtype, is_float_dtype as is_float_dtype, is_integer_dtype as is_integer_dtype, is_numeric_dtype as is_numeric_dtype, is_sparse as is_sparse, is_timedelta64_dtype as is_timedelta64_dtype, needs_i8_conversion as needs_i8_conversion
from pandas.core.dtypes.dtypes import CategoricalDtype as CategoricalDtype
from pandas.core.dtypes.missing import isna as isna, maybe_fill as maybe_fill
from pandas.core.frame import DataFrame as DataFrame
from pandas.core.generic import NDFrame as NDFrame
from pandas.core.groupby import grouper as grouper
from pandas.core.indexes.api import CategoricalIndex as CategoricalIndex, Index as Index, MultiIndex as MultiIndex, ensure_index as ensure_index
from pandas.core.series import Series as Series
from pandas.core.sorting import compress_group_index as compress_group_index, decons_obs_group_ids as decons_obs_group_ids, get_flattened_list as get_flattened_list, get_group_index as get_group_index, get_group_index_sorter as get_group_index_sorter, get_indexer_dict as get_indexer_dict
from pandas.errors import AbstractMethodError as AbstractMethodError
from pandas.util._decorators import cache_readonly as cache_readonly
from typing import Callable, Hashable, Iterator, Sequence

class WrappedCythonOp:
    cast_blocklist: Incomplete
    kind: Incomplete
    how: Incomplete
    has_dropped_na: Incomplete
    def __init__(self, kind: str, how: str, has_dropped_na: bool) -> None: ...
    def uses_mask(self) -> bool: ...
    def cython_operation(self, *, values: ArrayLike, axis: int, min_count: int = ..., comp_ids: np.ndarray, ngroups: int, **kwargs) -> ArrayLike: ...

class BaseGrouper:
    axis: Index
    group_keys: Incomplete
    mutated: Incomplete
    indexer: Incomplete
    dropna: Incomplete
    def __init__(self, axis: Index, groupings: Sequence[grouper.Grouping], sort: bool = ..., group_keys: bool = ..., mutated: bool = ..., indexer: Union[npt.NDArray[np.intp], None] = ..., dropna: bool = ...) -> None: ...
    @property
    def groupings(self) -> list[grouper.Grouping]: ...
    @property
    def shape(self) -> Shape: ...
    def __iter__(self) -> Iterator[Hashable]: ...
    @property
    def nkeys(self) -> int: ...
    def get_iterator(self, data: NDFrameT, axis: int = ...) -> Iterator[tuple[Hashable, NDFrameT]]: ...
    def group_keys_seq(self): ...
    def apply(self, f: Callable, data: Union[DataFrame, Series], axis: int = ...) -> tuple[list, bool]: ...
    def indices(self) -> dict[Hashable, npt.NDArray[np.intp]]: ...
    def result_ilocs(self) -> npt.NDArray[np.intp]: ...
    @property
    def codes(self) -> list[npt.NDArray[np.signedinteger]]: ...
    @property
    def levels(self) -> list[Index]: ...
    @property
    def names(self) -> list[Hashable]: ...
    def size(self) -> Series: ...
    def groups(self) -> dict[Hashable, np.ndarray]: ...
    def is_monotonic(self) -> bool: ...
    def has_dropped_na(self) -> bool: ...
    def group_info(self) -> tuple[npt.NDArray[np.intp], npt.NDArray[np.intp], int]: ...
    def codes_info(self) -> npt.NDArray[np.intp]: ...
    def ngroups(self) -> int: ...
    @property
    def reconstructed_codes(self) -> list[npt.NDArray[np.intp]]: ...
    def result_index(self) -> Index: ...
    def get_group_levels(self) -> list[ArrayLike]: ...
    def agg_series(self, obj: Series, func: Callable, preserve_dtype: bool = ...) -> ArrayLike: ...

class BinGrouper(BaseGrouper):
    bins: npt.NDArray[np.int64]
    binlabels: Index
    mutated: bool
    indexer: Incomplete
    def __init__(self, bins, binlabels, mutated: bool = ..., indexer: Incomplete | None = ...) -> None: ...
    def groups(self): ...
    @property
    def nkeys(self) -> int: ...
    def get_iterator(self, data: NDFrame, axis: int = ...): ...
    def indices(self): ...
    def group_info(self) -> tuple[npt.NDArray[np.intp], npt.NDArray[np.intp], int]: ...
    def reconstructed_codes(self) -> list[np.ndarray]: ...
    def result_index(self) -> Index: ...
    @property
    def levels(self) -> list[Index]: ...
    @property
    def names(self) -> list[Hashable]: ...
    @property
    def groupings(self) -> list[grouper.Grouping]: ...

class DataSplitter:
    data: Incomplete
    labels: Incomplete
    ngroups: Incomplete
    axis: Incomplete
    def __init__(self, data: NDFrameT, labels: npt.NDArray[np.intp], ngroups: int, axis: int = ...) -> None: ...
    def slabels(self) -> npt.NDArray[np.intp]: ...
    def __iter__(self): ...
    def sorted_data(self) -> NDFrameT: ...

class SeriesSplitter(DataSplitter): ...
class FrameSplitter(DataSplitter): ...

def get_splitter(data: NDFrame, labels: np.ndarray, ngroups: int, axis: int = ...) -> DataSplitter: ...
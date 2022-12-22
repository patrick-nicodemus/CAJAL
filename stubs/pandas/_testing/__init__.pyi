from _typeshed import Incomplete
from pandas import Categorical, CategoricalIndex, DataFrame, DatetimeIndex, Index, IntervalIndex, PeriodIndex, RangeIndex, Series, TimedeltaIndex
from pandas._config.localization import can_set_locale as can_set_locale, get_locales as get_locales, set_locale as set_locale
from pandas._testing._io import close as close, network as network, round_trip_localpath as round_trip_localpath, round_trip_pathlib as round_trip_pathlib, round_trip_pickle as round_trip_pickle, write_to_compressed as write_to_compressed
from pandas._testing._random import randbool as randbool, rands as rands
from pandas._testing._warnings import assert_produces_warning as assert_produces_warning, maybe_produces_warning as maybe_produces_warning
from pandas._testing.asserters import assert_almost_equal as assert_almost_equal, assert_attr_equal as assert_attr_equal, assert_categorical_equal as assert_categorical_equal, assert_class_equal as assert_class_equal, assert_contains_all as assert_contains_all, assert_copy as assert_copy, assert_datetime_array_equal as assert_datetime_array_equal, assert_dict_equal as assert_dict_equal, assert_equal as assert_equal, assert_extension_array_equal as assert_extension_array_equal, assert_frame_equal as assert_frame_equal, assert_index_equal as assert_index_equal, assert_indexing_slices_equivalent as assert_indexing_slices_equivalent, assert_interval_array_equal as assert_interval_array_equal, assert_is_sorted as assert_is_sorted, assert_is_valid_plot_return_object as assert_is_valid_plot_return_object, assert_metadata_equivalent as assert_metadata_equivalent, assert_numpy_array_equal as assert_numpy_array_equal, assert_period_array_equal as assert_period_array_equal, assert_series_equal as assert_series_equal, assert_sp_array_equal as assert_sp_array_equal, assert_timedelta_array_equal as assert_timedelta_array_equal, raise_assert_detail as raise_assert_detail
from pandas._testing.compat import get_dtype as get_dtype, get_obj as get_obj
from pandas._testing.contexts import RNGContext as RNGContext, decompress_file as decompress_file, ensure_clean as ensure_clean, ensure_clean_dir as ensure_clean_dir, ensure_safe_environment_variables as ensure_safe_environment_variables, set_timezone as set_timezone, use_numexpr as use_numexpr, with_csv_dialect as with_csv_dialect
from pandas._typing import Dtype
from pandas.core.api import Float64Index, Int64Index, NumericIndex, UInt64Index
from typing import Callable, ContextManager, Iterable

UNSIGNED_INT_NUMPY_DTYPES: list[Dtype]
UNSIGNED_INT_EA_DTYPES: list[Dtype]
SIGNED_INT_NUMPY_DTYPES: list[Dtype]
SIGNED_INT_EA_DTYPES: list[Dtype]
ALL_INT_NUMPY_DTYPES: Incomplete
ALL_INT_EA_DTYPES: Incomplete
FLOAT_NUMPY_DTYPES: list[Dtype]
FLOAT_EA_DTYPES: list[Dtype]
COMPLEX_DTYPES: list[Dtype]
STRING_DTYPES: list[Dtype]
DATETIME64_DTYPES: list[Dtype]
TIMEDELTA64_DTYPES: list[Dtype]
BOOL_DTYPES: list[Dtype]
BYTES_DTYPES: list[Dtype]
OBJECT_DTYPES: list[Dtype]
ALL_REAL_NUMPY_DTYPES: Incomplete
ALL_NUMPY_DTYPES: Incomplete
NARROW_NP_DTYPES: Incomplete
ENDIAN: Incomplete
NULL_OBJECTS: Incomplete
NP_NAT_OBJECTS: Incomplete
EMPTY_STRING_PATTERN: Incomplete

def set_testing_mode() -> None: ...
def reset_testing_mode() -> None: ...
def reset_display_options() -> None: ...
def equalContents(arr1, arr2) -> bool: ...
def box_expected(expected, box_cls, transpose: bool = ...): ...
def to_array(obj): ...
def getCols(k) -> str: ...
def makeStringIndex(k: int = ..., name: Incomplete | None = ...) -> Index: ...
def makeCategoricalIndex(k: int = ..., n: int = ..., name: Incomplete | None = ..., **kwargs) -> CategoricalIndex: ...
def makeIntervalIndex(k: int = ..., name: Incomplete | None = ..., **kwargs) -> IntervalIndex: ...
def makeBoolIndex(k: int = ..., name: Incomplete | None = ...) -> Index: ...
def makeNumericIndex(k: int = ..., name: Incomplete | None = ..., *, dtype) -> NumericIndex: ...
def makeIntIndex(k: int = ..., name: Incomplete | None = ...) -> Int64Index: ...
def makeUIntIndex(k: int = ..., name: Incomplete | None = ...) -> UInt64Index: ...
def makeRangeIndex(k: int = ..., name: Incomplete | None = ..., **kwargs) -> RangeIndex: ...
def makeFloatIndex(k: int = ..., name: Incomplete | None = ...) -> Float64Index: ...
def makeDateIndex(k: int = ..., freq: str = ..., name: Incomplete | None = ..., **kwargs) -> DatetimeIndex: ...
def makeTimedeltaIndex(k: int = ..., freq: str = ..., name: Incomplete | None = ..., **kwargs) -> TimedeltaIndex: ...
def makePeriodIndex(k: int = ..., name: Incomplete | None = ..., **kwargs) -> PeriodIndex: ...
def makeMultiIndex(k: int = ..., names: Incomplete | None = ..., **kwargs): ...
def index_subclass_makers_generator() -> None: ...
def all_timeseries_index_generator(k: int = ...) -> Iterable[Index]: ...
def make_rand_series(name: Incomplete | None = ..., dtype=...) -> Series: ...
def makeFloatSeries(name: Incomplete | None = ...) -> Series: ...
def makeStringSeries(name: Incomplete | None = ...) -> Series: ...
def makeObjectSeries(name: Incomplete | None = ...) -> Series: ...
def getSeriesData() -> dict[str, Series]: ...
def makeTimeSeries(nper: Incomplete | None = ..., freq: str = ..., name: Incomplete | None = ...) -> Series: ...
def makePeriodSeries(nper: Incomplete | None = ..., name: Incomplete | None = ...) -> Series: ...
def getTimeSeriesData(nper: Incomplete | None = ..., freq: str = ...) -> dict[str, Series]: ...
def getPeriodData(nper: Incomplete | None = ...) -> dict[str, Series]: ...
def makeTimeDataFrame(nper: Incomplete | None = ..., freq: str = ...) -> DataFrame: ...
def makeDataFrame() -> DataFrame: ...
def getMixedTypeDict(): ...
def makeMixedDataFrame() -> DataFrame: ...
def makePeriodFrame(nper: Incomplete | None = ...) -> DataFrame: ...
def makeCustomIndex(nentries, nlevels, prefix: str = ..., names: Union[bool, str, list[str], None] = ..., ndupe_l: Incomplete | None = ..., idx_type: Incomplete | None = ...) -> Index: ...
def makeCustomDataframe(nrows, ncols, c_idx_names: bool = ..., r_idx_names: bool = ..., c_idx_nlevels: int = ..., r_idx_nlevels: int = ..., data_gen_f: Incomplete | None = ..., c_ndupe_l: Incomplete | None = ..., r_ndupe_l: Incomplete | None = ..., dtype: Incomplete | None = ..., c_idx_type: Incomplete | None = ..., r_idx_type: Incomplete | None = ...) -> DataFrame: ...
def makeMissingDataframe(density: float = ..., random_state: Incomplete | None = ...) -> DataFrame: ...

class SubclassedSeries(Series): ...
class SubclassedDataFrame(DataFrame): ...
class SubclassedCategorical(Categorical): ...

def convert_rows_list_to_csv_str(rows_list: list[str]) -> str: ...
def external_error_raised(expected_exception: type[Exception]) -> ContextManager: ...
def get_cython_table_params(ndframe, func_names_and_expected): ...
def get_op_from_name(op_name: str) -> Callable: ...
def getitem(x): ...
def setitem(x): ...
def loc(x): ...
def iloc(x): ...
def at(x): ...
def iat(x): ...
def shares_memory(left, right) -> bool: ...
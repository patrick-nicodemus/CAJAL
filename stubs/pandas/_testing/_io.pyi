from _typeshed import Incomplete
from pandas import DataFrame as DataFrame, Series as Series
from pandas._testing._random import rands as rands
from pandas._testing.contexts import ensure_clean as ensure_clean
from pandas._typing import FilePath as FilePath, ReadPickleBuffer as ReadPickleBuffer
from pandas.compat import get_lzma_file as get_lzma_file
from pandas.compat._optional import import_optional_dependency as import_optional_dependency
from pandas.io.common import urlopen as urlopen
from typing import Any

def optional_args(decorator): ...
def network(t, url: str = ..., raise_on_error: bool = ..., check_before_test: bool = ..., error_classes: Incomplete | None = ..., skip_errnos=..., _skip_on_messages=...): ...
def can_connect(url, error_classes: Incomplete | None = ...) -> bool: ...
def round_trip_pickle(obj: Any, path: Union[FilePath, ReadPickleBuffer, None] = ...) -> Union[DataFrame, Series]: ...
def round_trip_pathlib(writer, reader, path: Union[str, None] = ...): ...
def round_trip_localpath(writer, reader, path: Union[str, None] = ...): ...
def write_to_compressed(compression, path, data, dest: str = ...) -> None: ...
def close(fignum: Incomplete | None = ...) -> None: ...
from _datetime import *
from _typeshed import Incomplete

MINYEAR: int
MAXYEAR: int

class timedelta:
    def __new__(cls, days: int = ..., seconds: int = ..., microseconds: int = ..., milliseconds: int = ..., minutes: int = ..., hours: int = ..., weeks: int = ...): ...
    def total_seconds(self): ...
    @property
    def days(self): ...
    @property
    def seconds(self): ...
    @property
    def microseconds(self): ...
    def __add__(self, other): ...
    __radd__: Incomplete
    def __sub__(self, other): ...
    def __rsub__(self, other): ...
    def __neg__(self): ...
    def __pos__(self): ...
    def __abs__(self): ...
    def __mul__(self, other): ...
    __rmul__: Incomplete
    def __floordiv__(self, other): ...
    def __truediv__(self, other): ...
    def __mod__(self, other): ...
    def __divmod__(self, other): ...
    def __eq__(self, other): ...
    def __le__(self, other): ...
    def __lt__(self, other): ...
    def __ge__(self, other): ...
    def __gt__(self, other): ...
    def __hash__(self): ...
    def __bool__(self) -> bool: ...
    def __reduce__(self): ...

class date:
    def __new__(cls, year, month: Incomplete | None = ..., day: Incomplete | None = ...): ...
    @classmethod
    def fromtimestamp(cls, t): ...
    @classmethod
    def today(cls): ...
    @classmethod
    def fromordinal(cls, n): ...
    @classmethod
    def fromisoformat(cls, date_string): ...
    @classmethod
    def fromisocalendar(cls, year, week, day): ...
    def ctime(self): ...
    def strftime(self, fmt): ...
    def __format__(self, fmt) -> str: ...
    def isoformat(self): ...
    @property
    def year(self): ...
    @property
    def month(self): ...
    @property
    def day(self): ...
    def timetuple(self): ...
    def toordinal(self): ...
    def replace(self, year: Incomplete | None = ..., month: Incomplete | None = ..., day: Incomplete | None = ...): ...
    def __eq__(self, other): ...
    def __le__(self, other): ...
    def __lt__(self, other): ...
    def __ge__(self, other): ...
    def __gt__(self, other): ...
    def __hash__(self): ...
    def __add__(self, other): ...
    __radd__: Incomplete
    def __sub__(self, other): ...
    def weekday(self): ...
    def isoweekday(self): ...
    def isocalendar(self): ...
    def __reduce__(self): ...

class tzinfo:
    def tzname(self, dt) -> None: ...
    def utcoffset(self, dt) -> None: ...
    def dst(self, dt) -> None: ...
    def fromutc(self, dt): ...
    def __reduce__(self): ...

class IsoCalendarDate(tuple):
    def __new__(cls, year, week, weekday): ...
    @property
    def year(self): ...
    @property
    def week(self): ...
    @property
    def weekday(self): ...
    def __reduce__(self): ...

class time:
    def __new__(cls, hour: int = ..., minute: int = ..., second: int = ..., microsecond: int = ..., tzinfo: Incomplete | None = ..., *, fold: int = ...): ...
    @property
    def hour(self): ...
    @property
    def minute(self): ...
    @property
    def second(self): ...
    @property
    def microsecond(self): ...
    @property
    def tzinfo(self): ...
    @property
    def fold(self): ...
    def __eq__(self, other): ...
    def __le__(self, other): ...
    def __lt__(self, other): ...
    def __ge__(self, other): ...
    def __gt__(self, other): ...
    def __hash__(self): ...
    def isoformat(self, timespec: str = ...): ...
    @classmethod
    def fromisoformat(cls, time_string): ...
    def strftime(self, fmt): ...
    def __format__(self, fmt) -> str: ...
    def utcoffset(self): ...
    def tzname(self): ...
    def dst(self): ...
    def replace(self, hour: Incomplete | None = ..., minute: Incomplete | None = ..., second: Incomplete | None = ..., microsecond: Incomplete | None = ..., tzinfo: bool = ..., *, fold: Incomplete | None = ...): ...
    def __reduce_ex__(self, protocol): ...
    def __reduce__(self): ...

class datetime(date):
    def __new__(cls, year, month: Incomplete | None = ..., day: Incomplete | None = ..., hour: int = ..., minute: int = ..., second: int = ..., microsecond: int = ..., tzinfo: Incomplete | None = ..., *, fold: int = ...): ...
    @property
    def hour(self): ...
    @property
    def minute(self): ...
    @property
    def second(self): ...
    @property
    def microsecond(self): ...
    @property
    def tzinfo(self): ...
    @property
    def fold(self): ...
    @classmethod
    def fromtimestamp(cls, t, tz: Incomplete | None = ...): ...
    @classmethod
    def utcfromtimestamp(cls, t): ...
    @classmethod
    def now(cls, tz: Incomplete | None = ...): ...
    @classmethod
    def utcnow(cls): ...
    @classmethod
    def combine(cls, date, time, tzinfo: bool = ...): ...
    @classmethod
    def fromisoformat(cls, date_string): ...
    def timetuple(self): ...
    def timestamp(self): ...
    def utctimetuple(self): ...
    def date(self): ...
    def time(self): ...
    def timetz(self): ...
    def replace(self, year: Incomplete | None = ..., month: Incomplete | None = ..., day: Incomplete | None = ..., hour: Incomplete | None = ..., minute: Incomplete | None = ..., second: Incomplete | None = ..., microsecond: Incomplete | None = ..., tzinfo: bool = ..., *, fold: Incomplete | None = ...): ...
    def astimezone(self, tz: Incomplete | None = ...): ...
    def ctime(self): ...
    def isoformat(self, sep: str = ..., timespec: str = ...): ...
    @classmethod
    def strptime(cls, date_string, format): ...
    def utcoffset(self): ...
    def tzname(self): ...
    def dst(self): ...
    def __eq__(self, other): ...
    def __le__(self, other): ...
    def __lt__(self, other): ...
    def __ge__(self, other): ...
    def __gt__(self, other): ...
    def __add__(self, other): ...
    __radd__: Incomplete
    def __sub__(self, other): ...
    def __hash__(self): ...
    def __reduce_ex__(self, protocol): ...
    def __reduce__(self): ...

class timezone(tzinfo):
    def __new__(cls, offset, name=...): ...
    def __getinitargs__(self): ...
    def __eq__(self, other): ...
    def __hash__(self): ...
    def utcoffset(self, dt): ...
    def tzname(self, dt): ...
    def dst(self, dt) -> None: ...
    def fromutc(self, dt): ...
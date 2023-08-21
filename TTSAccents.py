from enum import Enum, auto


class MetaAccentEnum(Enum):
    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, lang_code: str, short_name: str, long_name: str = None):
        self._lang_code_ = lang_code
        self._short_name_ = short_name
        self._long_name_ = long_name

    # this makes sure that these are read-only
    @property
    def lang_code(self) -> str:
        return self._lang_code_

    @property
    def short_name(self) -> str:
        return self._short_name_

    @property
    def long_name(self) -> str:
        return self._long_name_


class AccentEnum(MetaAccentEnum):
    US = auto(), "com", "US", "United States"
    AU = auto(), "com.au", "AU", "Australia"
    UK = auto(), "co.uk", "UK", "United Kingdom"
    CA = auto(), "ca", "CA", "Canada"
    IN = auto(), "co.in", "IN", "India"
    IE = auto(), "ie", "IE", "Ireland"
    SA = auto(), "co.za", "SA", "South Africa"


class TTSAccents:
    @property
    def current_accent(self) -> AccentEnum:
        return self._current_accent

    @current_accent.setter
    def current_accent(self, new_accent: AccentEnum):
        self._current_accent = new_accent

    def __init__(self, accent: AccentEnum = AccentEnum.US) -> None:
        self._current_accent = accent

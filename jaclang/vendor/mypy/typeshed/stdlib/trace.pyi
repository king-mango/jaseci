import sys
import types
from _typeshed import StrPath, TraceFunction
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeVar
from typing_extensions import ParamSpec, TypeAlias

__all__ = ["Trace", "CoverageResults"]

_T = TypeVar("_T")
_P = ParamSpec("_P")
_FileModuleFunction: TypeAlias = tuple[str, str | None, str]

class CoverageResults:
    def __init__(
        self,
        counts: dict[tuple[str, int], int] | None = None,
        calledfuncs: dict[_FileModuleFunction, int] | None = None,
        infile: StrPath | None = None,
        callers: (
            dict[tuple[_FileModuleFunction, _FileModuleFunction], int] | None
        ) = None,
        outfile: StrPath | None = None,
    ) -> None: ...  # undocumented
    def update(self, other: CoverageResults) -> None: ...
    def write_results(
        self,
        show_missing: bool = True,
        summary: bool = False,
        coverdir: StrPath | None = None,
    ) -> None: ...
    def write_results_file(
        self,
        path: StrPath,
        lines: Sequence[str],
        lnotab: Any,
        lines_hit: Mapping[int, int],
        encoding: str | None = None,
    ) -> tuple[int, int]: ...
    def is_ignored_filename(self, filename: str) -> bool: ...  # undocumented

class Trace:
    def __init__(
        self,
        count: int = 1,
        trace: int = 1,
        countfuncs: int = 0,
        countcallers: int = 0,
        ignoremods: Sequence[str] = (),
        ignoredirs: Sequence[str] = (),
        infile: StrPath | None = None,
        outfile: StrPath | None = None,
        timing: bool = False,
    ) -> None: ...
    def run(self, cmd: str | types.CodeType) -> None: ...
    def runctx(
        self,
        cmd: str | types.CodeType,
        globals: Mapping[str, Any] | None = None,
        locals: Mapping[str, Any] | None = None,
    ) -> None: ...
    if sys.version_info >= (3, 9):
        def runfunc(
            self, __func: Callable[_P, _T], *args: _P.args, **kw: _P.kwargs
        ) -> _T: ...
    else:
        def runfunc(
            self, func: Callable[_P, _T], *args: _P.args, **kw: _P.kwargs
        ) -> _T: ...

    def file_module_function_of(
        self, frame: types.FrameType
    ) -> _FileModuleFunction: ...
    def globaltrace_trackcallers(
        self, frame: types.FrameType, why: str, arg: Any
    ) -> None: ...
    def globaltrace_countfuncs(
        self, frame: types.FrameType, why: str, arg: Any
    ) -> None: ...
    def globaltrace_lt(self, frame: types.FrameType, why: str, arg: Any) -> None: ...
    def localtrace_trace_and_count(
        self, frame: types.FrameType, why: str, arg: Any
    ) -> TraceFunction: ...
    def localtrace_trace(
        self, frame: types.FrameType, why: str, arg: Any
    ) -> TraceFunction: ...
    def localtrace_count(
        self, frame: types.FrameType, why: str, arg: Any
    ) -> TraceFunction: ...
    def results(self) -> CoverageResults: ...

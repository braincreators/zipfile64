"""Public package interface for the patched :mod:`zipfile` API."""

from __future__ import annotations

import zipfile as _zipfile
from typing import Any

from zipfile64.support import (
    Deflate64Compressor,
    Deflate64Decompressor,
    ZIP_DEFLATE64,
    is_patched,
    patch,
    patched,
    unpatch,
)

__all__ = [
    "Deflate64Compressor",
    "Deflate64Decompressor",
    "ZIP_DEFLATE64",
    "is_patched",
    "patch",
    "patched",
    "unpatch",
]

patch()


def __getattr__(name: str) -> Any:
    return getattr(_zipfile, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_zipfile)))

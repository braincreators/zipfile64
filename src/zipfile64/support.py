"""Deflate64 support for Python's :mod:`zipfile` module."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import threading
from typing import Any, cast
import zipfile
import inflate64

ZIP_DEFLATE64 = 9

__all__ = [
    "ZIP_DEFLATE64",
    "Deflate64Compressor",
    "Deflate64Decompressor",
    "is_patched",
    "main",
    "patch",
    "patched",
    "unpatch",
]

_PATCH_LOCK = threading.RLock()
_ZIPFILE = cast(Any, zipfile)
_ORIGINAL_CHECK_COMPRESSION = _ZIPFILE._check_compression
_ORIGINAL_GET_COMPRESSOR = _ZIPFILE._get_compressor
_ORIGINAL_GET_DECOMPRESSOR = _ZIPFILE._get_decompressor
_HAS_ORIGINAL_CONSTANT = hasattr(zipfile, "ZIP_DEFLATE64")
_ORIGINAL_CONSTANT = getattr(zipfile, "ZIP_DEFLATE64", None)


class Deflate64Compressor:
    """Adapter that makes :class:`inflate64.Deflater` look like zipfile expects."""

    def __init__(self, compresslevel: int | None = None) -> None:
        self._compresslevel = compresslevel
        self._compressor = inflate64.Deflater()

    def compress(self, data: bytes | bytearray | memoryview) -> bytes:
        return self._compressor.deflate(bytes(data))

    def flush(self) -> bytes:
        return self._compressor.flush()


class Deflate64Decompressor:
    """Adapter that makes :class:`inflate64.Inflater` look like zipfile expects."""

    def __init__(self) -> None:
        self._decompressor = inflate64.Inflater()

    @property
    def eof(self) -> bool:
        return self._decompressor.eof

    def decompress(
        self, data: bytes | bytearray | memoryview, max_length: int = 0
    ) -> bytes:
        return self._decompressor.inflate(bytes(data), max_length=max_length)

    def flush(self) -> bytes:
        return b""


def _check_compression(compression: int) -> None:
    if compression == ZIP_DEFLATE64:
        return
    _ORIGINAL_CHECK_COMPRESSION(compression)


def _get_compressor(compress_type: int, compresslevel: int | None = None):
    if compress_type == ZIP_DEFLATE64:
        return Deflate64Compressor(compresslevel=compresslevel)
    return _ORIGINAL_GET_COMPRESSOR(compress_type, compresslevel)


def _get_decompressor(compress_type: int):
    if compress_type == ZIP_DEFLATE64:
        return Deflate64Decompressor()
    return _ORIGINAL_GET_DECOMPRESSOR(compress_type)


def is_patched() -> bool:
    """Return ``True`` when :mod:`zipfile` has Deflate64 support installed."""

    return _ZIPFILE._get_decompressor is _get_decompressor


def patch() -> None:
    """Install Deflate64 support into the standard-library :mod:`zipfile` module."""

    with _PATCH_LOCK:
        if is_patched():
            return

        _ZIPFILE.ZIP_DEFLATE64 = ZIP_DEFLATE64
        _ZIPFILE.compressor_names[ZIP_DEFLATE64] = "deflate64"
        _ZIPFILE._check_compression = _check_compression
        _ZIPFILE._get_compressor = _get_compressor
        _ZIPFILE._get_decompressor = _get_decompressor


def unpatch() -> None:
    """Restore the original :mod:`zipfile` behavior."""

    with _PATCH_LOCK:
        if not is_patched():
            return

        _ZIPFILE._check_compression = _ORIGINAL_CHECK_COMPRESSION
        _ZIPFILE._get_compressor = _ORIGINAL_GET_COMPRESSOR
        _ZIPFILE._get_decompressor = _ORIGINAL_GET_DECOMPRESSOR
        _ZIPFILE.compressor_names[ZIP_DEFLATE64] = "deflate64"

        if _HAS_ORIGINAL_CONSTANT:
            _ZIPFILE.ZIP_DEFLATE64 = _ORIGINAL_CONSTANT
        else:
            delattr(_ZIPFILE, "ZIP_DEFLATE64")


@contextmanager
def patched() -> Iterator[None]:
    """Context manager that enables Deflate64 support for a limited scope."""

    patch()
    try:
        yield
    finally:
        unpatch()


def main(args: list[str] | None = None) -> None:
    """Run the standard zipfile CLI with Deflate64 support enabled."""

    patch()
    _ZIPFILE.main(args)

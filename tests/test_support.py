from __future__ import annotations

import io
import struct
import zlib
import zipfile

import inflate64

import zipfile64.support


def build_deflate64_zip(filename: str, data: bytes) -> bytes:
    compressor = inflate64.Deflater()
    compressed = compressor.deflate(data) + compressor.flush()
    encoded_name = filename.encode("utf-8")
    crc = zlib.crc32(data) & 0xFFFFFFFF

    local_header = struct.pack(
        "<4s2B4HL2L2H",
        b"PK\x03\x04",
        20,
        0,
        0,
        zipfile64.support.ZIP_DEFLATE64,
        0,
        0,
        crc,
        len(compressed),
        len(data),
        len(encoded_name),
        0,
    )
    local_record = local_header + encoded_name + compressed

    central_header = struct.pack(
        "<4s4B4HL2L5H2L",
        b"PK\x01\x02",
        20,
        3,
        20,
        3,
        0,
        zipfile64.support.ZIP_DEFLATE64,
        0,
        0,
        crc,
        len(compressed),
        len(data),
        len(encoded_name),
        0,
        0,
        0,
        0,
        0,
        0,
    )
    central_directory = central_header + encoded_name

    end_record = struct.pack(
        "<4s4H2LH",
        b"PK\x05\x06",
        0,
        0,
        1,
        1,
        len(central_directory),
        len(local_record),
        0,
    )
    return local_record + central_directory + end_record


def test_patch_is_reversible() -> None:

    with zipfile64.support.patched():
        assert zipfile64.support.is_patched()
        assert zipfile.ZIP_DEFLATE64 == zipfile64.support.ZIP_DEFLATE64  # type: ignore[attr-defined]

    assert not zipfile64.support.is_patched()


def test_can_read_deflate64_archive() -> None:
    with zipfile64.support.patched():
        archive = build_deflate64_zip("example.txt", b"deflate64 works" * 64)

        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            assert zf.read("example.txt") == b"deflate64 works" * 64


def test_can_write_deflate64_archive() -> None:
    with zipfile64.support.patched():
        buffer = io.BytesIO()
        payload = b"hello from zipfile-d64" * 128

        with zipfile.ZipFile(
            buffer, mode="w", compression=zipfile64.support.ZIP_DEFLATE64
        ) as zf:
            zf.writestr("payload.txt", payload)

        buffer.seek(0)

        with zipfile.ZipFile(buffer, mode="r") as zf:
            info = zf.getinfo("payload.txt")
            assert info.compress_type == zipfile64.support.ZIP_DEFLATE64
            assert zf.read("payload.txt") == payload

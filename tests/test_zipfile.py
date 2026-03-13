import importlib
import zipfile
import zipfile64.support


def test_module_is_patched_on_import() -> None:
    assert not zipfile64.support.is_patched()
    importlib.import_module("zipfile64.zipfile")
    assert zipfile64.support.is_patched()
    assert zipfile.ZIP_DEFLATE64 == zipfile64.support.ZIP_DEFLATE64  # type: ignore[attr-defined]

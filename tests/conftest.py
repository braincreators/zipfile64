from __future__ import annotations

import importlib
import zipfile

import pytest

import zipfile64.support


@pytest.fixture(autouse=True)
def clean_patch_state():
    yield
    # Restore the original state in case the module is patched elsewhere
    importlib.reload(zipfile)
    importlib.reload(zipfile64.support)

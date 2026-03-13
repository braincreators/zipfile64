# zipfile64

Adds Deflate64 support to Python's standard `zipfile` module.

## Features

- reads ZIP archives that use compression method `9` (Deflate64)
- writes ZIP archives with Deflate64 when requested
- keeps the standard `zipfile` API
- uses `uv` for dependency and virtualenv management


## Getting started

Example using pip:
```bash
pip install zipfile64
```


## Usage

```python
# Importing zipfile64.zipfile will patch the built-in zipfile module
import zipfile64.zipfile as zipfile


with zipfile.ZipFile("archive.zip") as zf:
	print(zf.namelist())
	data = zf.read("example.txt")
```

Writing a Deflate64 archive:

```python
import io
import zipfile

from zipfile64 import ZIP_DEFLATE64, patch

patch()

buffer = io.BytesIO()
with zipfile.ZipFile(buffer, mode="w", compression=ZIP_DEFLATE64) as zf:
	zf.writestr("hello.txt", b"hello world")
```

You can also use the patched python zipfile CLI:

- `uv run zipfile64 -l archive.zip`
- `uv run zipfile64 -e archive.zip output-dir`

## Development

Create the virtual environment and install dependencies with `uv`:

- `uv sync`
- `uv sync --group dev` for test dependencies

`uv` will create the local virtual environment for the project.

- `uv run pytest`

## Limitations

- patching is process-wide because it extends the standard-library module
- Deflate64 compression level is currently ignored by the backend library

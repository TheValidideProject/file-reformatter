# file-reformatter

A simple CLI utility to convert HEIC/HEIF images to PNG.

## Usage

```
python reformat.py SOURCE [DEST] [--overwrite]
```

- `SOURCE` can be an individual image file or a directory containing `.heic` or `.heif` files.
- If `SOURCE` is a directory, images are converted recursively. `DEST` defaults to `SOURCE`.
- If `SOURCE` is a file, `DEST` defaults to the same path with a `.png` extension.
- Use `--overwrite` to overwrite existing files.

Example:

```
python reformat.py image.heic
python reformat.py pictures/ converted/ --overwrite
```

## Drag-and-drop website

Run the Flask server to use a web interface for converting images. After starting the server, open `http://localhost:5000` and drop one or more `.heic`/`.heif` files onto the page. The converted images will be downloaded automatically.

```bash
python webapp.py
```

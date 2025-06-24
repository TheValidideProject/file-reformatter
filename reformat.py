import os
import click
from PIL import Image
import pyheif


def convert(src: str, dest: str, overwrite: bool = False) -> None:
    """Convert a single HEIC/HEIF image to PNG."""
    if not overwrite and os.path.exists(dest):
        raise FileExistsError(f"{dest} already exists. Use --overwrite to replace it.")
    heif_file = pyheif.read(src)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
    )
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    image.save(dest, "PNG")
    print(f"Converted {src} -> {dest}")


@click.command()
@click.argument("source")
@click.argument("dest", required=False)
@click.option("--overwrite", is_flag=True, help="Overwrite destination files if they exist")
def main(source: str, dest: str | None, overwrite: bool) -> None:
    """Convert HEIC images to PNG.

    SOURCE can be a file or directory. If it is a directory, all .heic files will
    be converted recursively into DEST (defaults to SOURCE).
    """
    if os.path.isdir(source):
        if dest is None:
            dest = source
        for root, _, files in os.walk(source):
            for name in files:
                if name.lower().endswith((".heic", ".heif")):
                    src_path = os.path.join(root, name)
                    rel = os.path.relpath(src_path, source)
                    dest_path = os.path.join(dest, os.path.splitext(rel)[0] + ".png")
                    convert(src_path, dest_path, overwrite)
    else:
        if dest is None:
            base, _ = os.path.splitext(source)
            dest = base + ".png"
        convert(source, dest, overwrite)


if __name__ == "__main__":
    main()

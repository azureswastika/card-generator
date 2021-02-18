from pathlib import Path
from random import choices
from string import ascii_letters

upload_dir = Path(__file__).parent.joinpath("static")
upload_dir.mkdir(exist_ok=True)


def process_path(name: str, path: Path):
    if path.exists():
        path = upload_dir.joinpath(
            name,
            f"{path.stem}{''.join(choices(ascii_letters))}{path.suffix}",
        )
        path = Path(process_path(name, path))
    return path

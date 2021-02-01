from pathlib import Path

from PIL import Image


class Base:
    def __init__(self, fp: Path) -> None:
        self._image = Image.open(fp)
        self.image = self._image
        self.w, self.h = self.image.size


class Inplace:
    def __init__(self, fp: Path) -> None:
        self.image = Image.open(fp)
        self.w, self.h = self.image.size

def main(base: str):
    img = Base(base)
    for i in Path('images').glob('*'):
        img.save(f'{i.stem}.jpg')

main('src/base.jpg')

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class Inplace:
    def __init__(self, fp: Path) -> None:
        self.path = fp
        self.image = Image.open(fp)
        self.w, self.h = self.image.size


class Base:
    white = (0, 0, 0, 0)
    header = ImageFont.truetype("src/Oswald-Regular.ttf", 50)
    paragraph = ImageFont.truetype("src/Oswald-Regular.ttf", 14)
    text = list(
        filter(bool, open("src/data.txt", encoding="utf-8").read().split(":::"))
    )
    text = [i.split("|||") for i in text]

    def __init__(self, fp: Path) -> None:
        self._image = Image.open(fp)
        self.image = self._image.copy()
        self.w, self.h = self.image.size

    def paste(self) -> None:
        for i, el in enumerate(Path("images").glob("*")):
            inplace = Inplace(el)

            box = ((self.w - inplace.w) // 2, (self.h - inplace.h) // 2 - 200)
            self.image.paste(inplace.image, box)

            draw = ImageDraw.Draw(self.image)

            # card numeration
            w, h = draw.textsize(str(i + 1), self.header)
            draw.text(
                (112 - w // 2, 112 - h // 1.5),
                str(i + 1),
                font=self.header,
                fill=self.white,
            )

            # card header
            w, h = draw.textsize(self.text[i][0], self.header)
            draw.text(
                (470 - w // 2, 920 - h // 1.5),
                self.text[i][0],
                font=self.header,
                fill=self.white,
            )

            # card desc 1
            draw.text(
                (90, 940),
                self.text[i][1],
                font=self.paragraph,
                fill=self.white,
            )

            # card desc 2
            draw.text(
                (490, 940),
                self.text[i][2],
                font=self.paragraph,
                fill=self.white,
            )

            self.image.convert('RGB').save(f"{inplace.path.stem}.jpg")
            self.reset()

    def reset(self) -> None:
        self.image = self._image.copy()


img = Base("src/base.jpg")
img.paste()

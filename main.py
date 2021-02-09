from pathlib import Path
from textwrap import fill, wrap

from PIL import Image, ImageDraw, ImageFont

SRC_BACKEND_IMG = "src/backend.jpg"
SRC_MAIN_IMG = "src/main.jpg"
SRC_FRONTEND_IMG = "src/frontend.jpg"
OUTPUT_DIR = "output"
DATA_DIR = "static"

FFORMAT = "png"
CONVERT = "RGB"


class Base:
    def __init__(self, fp: str) -> None:
        self._image = Image.open(fp)
        self.image = self._image.copy()
        self.w, self.h = self.image.size

    def reset(self) -> None:
        self.image = self._image.copy()


class Geneartor:
    static = Path(DATA_DIR)
    output = Path(OUTPUT_DIR)
    output.mkdir(exist_ok=True)

    backend = Base(SRC_BACKEND_IMG)
    main = Base(SRC_MAIN_IMG)
    frontend = Base(SRC_FRONTEND_IMG)

    header = ImageFont.truetype("src/Oswald-Regular.ttf", 55)
    paragraph = ImageFont.truetype("src/Oswald-Regular.ttf", 15)
    white = "white"
    black = (0, 0, 0, 0)
    blue = (40, 101, 176, 0)

    def __init__(self, obj) -> None:
        self.name = obj.name
        self.output.joinpath(self.name).mkdir(exist_ok=True)
        self.output.joinpath(self.name, "frontend").mkdir(exist_ok=True)
        self.title = self.process_text(obj.backend.title)
        self.f_backend = Image.open(self.static.joinpath(obj.backend.backend))
        if self.f_backend.width > 710 or self.f_backend.height > 590:
            self.f_backend.thumbnail((710, 590), Image.ANTIALIAS)
        self.f_main = Image.open(self.static.joinpath(obj.backend.main))
        if self.f_main.width > 710 or self.f_main.height > 590:
            self.f_main.thumbnail((710, 590), Image.ANTIALIAS)
        self.cards = obj.cards

    def start(self) -> None:
        self.create_backend()
        self.create_frontend()
        self.create_main()

    def create_backend(self) -> None:
        box = (
            (self.backend.w - self.f_backend.width) // 2,
            (self.backend.h - self.f_backend.height) // 2,
        )
        try:
            self.backend.image.paste(self.f_backend, box, self.f_backend)
        except ValueError:
            self.backend.image.paste(
                self.f_backend, box, self.f_backend.convert("RGBA")
            )
        draw = ImageDraw.Draw(self.backend.image)
        draw = self.add_title(draw, self.title, self.blue, 1150)
        self.backend.image.convert(CONVERT).save(
            self.output.joinpath(f"{self.name}/backend.{FFORMAT}")
        )
        self.backend.reset()

    def create_main(self) -> None:
        box = (
            self.main.w // 2 - self.f_main.width // 2,
            self.main.h // 2 - self.f_main.height // 2,
        )
        try:
            self.main.image.paste(self.f_main, box, self.f_main)
        except ValueError:
            self.main.image.paste(self.f_main, box, self.f_main.convert("RGBA"))
        draw = ImageDraw.Draw(self.main.image)

        w, h = draw.textsize("0", self.header)
        box = (112 - w // 2, 112 - h // 1.5)
        draw.text(
            box, "0", font=self.header, fill=self.white,
        )

        self.main.image.convert(CONVERT).save(
            self.output.joinpath(f"{self.name}/main.{FFORMAT}")
        )
        self.main.reset()

    def create_frontend(self):
        for el in self.cards:
            image = Image.open(self.static.joinpath(el.image))
            if image.width > 710 or image.height > 590:
                image.thumbnail((710, 590), Image.ANTIALIAS)
            box = (
                (self.frontend.w - image.width) // 2,
                (self.frontend.h - image.height) // 2 - 200,
            )
            try:
                self.frontend.image.paste(image, box, image)
            except ValueError:
                self.frontend.image.paste(image, box, image.convert("RGBA"))

            draw = ImageDraw.Draw(self.frontend.image)

            w, h = draw.textsize(str(el.num), self.header)
            box = (112 - w // 2, 112 - h // 1.5)
            draw.text(box, str(el.num), font=self.header, fill=self.black)
            title = self.process_text(el.title)
            draw = self.add_title(draw, title, self.black)

            draw.multiline_text(
                (90, 960), fill(el.block1, 58), font=self.paragraph, fill=self.black,
            )

            draw.multiline_text(
                (490, 960), fill(el.block2, 58), font=self.paragraph, fill=self.black,
            )

            self.frontend.image.convert(CONVERT).save(
                f"{OUTPUT_DIR}/{self.name}/frontend/{el.num}.{FFORMAT}"
            )
            self.frontend.reset()

    def add_title(self, draw, title, fill, heigth=None):
        if list(title).count("\n") >= 2:
            n_count = list(title).count("\n")
            title = self.process_text(title, 35 + 5 * n_count)
            subheader = ImageFont.truetype("src/Oswald-Regular.ttf", 55 - 5 * n_count)
            w, h = draw.textsize(title, subheader)
            box = self.process_heigth(w, h, heigth)
            draw.multiline_text(box, title, font=subheader, fill=fill, align="center")
            return draw
        w, h = draw.textsize(title, self.header)
        box = self.process_heigth(w, h, heigth)
        draw.multiline_text(
            box, title, font=self.header, fill=fill, align="center",
        )
        return draw

    def process_heigth(self, w, h, heigth):
        if heigth:
            return ((self.frontend.w - w) / 2, heigth - h / 2)
        return ((self.frontend.w - w) / 2, (self.frontend.h - h) / 2 + 150)

    @staticmethod
    def process_text(text, width=35):
        return "\n".join(line for line in wrap(text, width))

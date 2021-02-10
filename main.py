from pathlib import Path
from textwrap import fill, wrap
from threading import Thread

from PIL import Image, ImageDraw, ImageFont

SRC_BACKEND_IMG = "src/backend.jpg"
SRC_MAIN_IMG = "src/main.jpg"
SRC_FRONTEND_IMG = "src/frontend.jpg"
OUTPUT_DIR = "output"
DATA_DIR = "static"

BACKEND_IMG = "backend.jpg"
MAIN_IMG = "main.jpg"
FRONTEND_DIR = "frontend"
TEXT_FILE = "data.txt"

FFORMAT = "jpg"
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
    white = (255, 255, 255, 0)
    blue = (40, 101, 176, 0)
    white2 = (0, 0, 0, 0)

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
        Thread(target=self.create_backend, daemon=True).start()
        Thread(target=self.create_main, daemon=True).start()
        Thread(target=self.create_frontend, daemon=True).start()

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
        if list(self.title).count("\n") >= 2:
            n_count = list(self.title).count("\n")
            self.title = self.process_text(self.title, 35 + 5 * n_count)
            subheader = ImageFont.truetype("src/Oswald-Regular.ttf", 55 - 5 * n_count)
            self.title = self.process_text(self.title, 40)
            w, h = draw.textsize(self.title, subheader)
            box = ((self.backend.w - w) / 2, 1150 - h / 2)
            draw.multiline_text(
                box, self.title, font=subheader, fill=self.blue, align="center"
            )
        else:
            w, h = draw.textsize(self.title, self.header)
            box = ((self.backend.w - w) / 2, 1150 - h / 2)
            draw.multiline_text(
                box, self.title, font=self.header, fill=self.blue, align="center"
            )
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

        # adding header on main.jpg
        # w, h = draw.textsize(obj.text.title, self.header)
        # box = (470 - w // 2, 1150 - h // 2)
        # draw.text(
        #     box, obj.text.title, font=self.header, fill=self.white,
        # )

        self.main.image.convert(CONVERT).save(
            self.output.joinpath(f"{self.name}/main.{FFORMAT}")
        )
        self.main.reset()

    def create_frontend(self):
        for i, el in enumerate(self.cards):
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

            w, h = draw.textsize(str(i + 1), self.header)
            box = (112 - w // 2, 112 - h // 1.5)
            draw.text(box, str(i + 1), font=self.header, fill=self.white2)
            title = self.process_text(el.title)
            if list(title).count("\n") >= 2:
                n_count = list(title).count("\n")
                title = self.process_text(el.title, 35 + 5 * n_count)
                subheader = ImageFont.truetype("src/Oswald-Regular.ttf", 55 - 5 * n_count)
                w, h = draw.textsize(title, subheader)
                box = ((self.frontend.w - w) / 2, (self.frontend.h - h) / 2 + 150)
                draw.multiline_text(
                    box,
                    title,
                    font=subheader,
                    fill=self.white2,
                    align="center",
                )
            else:
                w, h = draw.textsize(title, self.header)
                box = ((self.frontend.w - w) / 2, (self.frontend.h - h) / 2 + 150)
                draw.multiline_text(
                    box, title, font=self.header, fill=self.white2, align="center",
                )

            draw.multiline_text(
                (90, 960),
                fill(el.block1, 70, break_long_words=True),
                font=self.paragraph,
                fill=self.white2,
            )

            draw.multiline_text(
                (490, 960),
                fill(el.block2, 70, break_long_words=True),
                font=self.paragraph,
                fill=self.white2,
            )

            self.frontend.image.convert(CONVERT).save(
                f"{OUTPUT_DIR}/{self.name}/frontend/{i}.{FFORMAT}"
            )
            self.frontend.reset()
    #доделать
    def create_pdf(self):
        image1 = Image.open('1.png')
        im1 = image1.convert('RGB')
        im1.save('1.pdf')

    @staticmethod
    def process_text(text, width=35):
        return "\n".join(line for line in wrap(text, width))

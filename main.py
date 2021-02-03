from pathlib import Path

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

    header = ImageFont.truetype("src/Oswald-Regular.ttf", 60)
    paragraph = ImageFont.truetype("src/Oswald-Regular.ttf", 14)
    white = (255, 255, 255, 0)
    blue = (40, 101, 176, 0)
    white2 = (0, 0, 0, 0)

    def __init__(self, obj) -> None:
        self.name = obj.name
        self.output.joinpath(self.name).mkdir(exist_ok=True)
        self.output.joinpath(self.name, "frontend").mkdir(exist_ok=True)
        self.title = obj.backend.title
        self.f_backend = Image.open(self.static.joinpath(obj.backend.backend))
        if self.f_backend.width > 710 or self.f_backend.height > 590:
            self.f_backend.thumbnail((710, 590), Image.ANTIALIAS)
        self.f_main = Image.open(self.static.joinpath(obj.backend.main))
        if self.f_main.width > 710 or self.f_main.height > 590:
            self.f_main.thumbnail((710, 590), Image.ANTIALIAS)
        self.cards = obj.cards

    def start(self) -> None:
        self.create_backend()
        self.create_main()
        self.create_frontend()

    def create_backend(self) -> None:
        box = (
            self.backend.w // 2 - self.f_backend.width // 2,
            self.backend.h // 2 - self.f_backend.height // 2,
        )
        try:
            self.backend.image.paste(self.f_backend, box, self.f_backend)
        except ValueError:
            self.backend.image.paste(
                self.f_backend, box, self.f_backend.convert("RGBA")
            )
        draw = ImageDraw.Draw(self.backend.image)
        w, h = draw.textsize(self.title, self.header)
        box = (470 - w // 2, 1150 - h // 2)
        draw.text(
            box, self.title, font=self.header, fill=self.blue,
        )
        self.backend.image.convert("RGB").save(
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

        self.main.image.convert("RGB").save(
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

            # card numeration
            w, h = draw.textsize(str(i + 1), self.header)
            box = (112 - w // 2, 112 - h // 1.5)
            draw.text(box, str(i + 1), font=self.header, fill=self.white2)

            # card header
            w, h = draw.textsize(el.title, self.header)
            box = (470 - w // 2, 880 - h // 2)
            draw.text(
                box, el.title, font=self.header, fill=self.white2,
            )

            # card desc 1
            draw.text(
                (90, 960), el.block1, font=self.paragraph, fill=self.white2,
            )

            # card desc 2
            draw.text(
                (490, 960), el.block2, font=self.paragraph, fill=self.white2,
            )

            self.frontend.image.convert("RGB").save(
                f"{OUTPUT_DIR}/{self.name}/frontend/{i}.{FFORMAT}"
            )
            self.frontend.reset()

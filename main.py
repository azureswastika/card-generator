from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC_BACKEND_IMG = "src/backend.jpg"
SRC_MAIN_IMG = "src/main.jpg"
SRC_FRONTEND_IMG = "src/frontend.jpg"
OUTPUT_DIR = "output"
DATA_DIR = "data"

BACKEND_IMG = "backend.jpg"
MAIN_IMG = "main.jpg"
FRONTEND_DIR = "frontend"
TEXT_FILE = "data.txt"

FFORMAT = ".jpg"


class Base:
    def __init__(self, fp: str) -> None:
        self._image = Image.open(fp)
        self.image = self._image.copy()
        self.w, self.h = self.image.size

    def reset(self) -> None:
        self.image = self._image.copy()


class Inplace:
    def __init__(self, fp: Path) -> None:
        self.path = fp
        self.image = Image.open(fp)
        self.w, self.h = self.image.size


class Text:
    def __init__(self, fp: Path) -> None:
        text = open(fp, encoding="utf-8").read().split(":::")
        text = [i.split("|||") for i in list(filter(bool, text))]
        if len(text[0]) == 1:
            self.title = text[0].pop(0)
        else:
            self.title = "None"
        self.text = list(filter(bool, text))


class Folder:
    def __init__(self, fp: Path) -> None:
        self.path = fp
        self.dirname = fp.stem
        self.backend = Inplace(fp.joinpath(BACKEND_IMG))
        self.main = Inplace(fp.joinpath(MAIN_IMG))
        self.frontend = [Inplace(i) for i in fp.joinpath(FRONTEND_DIR).glob("*")]
        self.text = Text(fp.joinpath(TEXT_FILE))
        dirr = Path(OUTPUT_DIR).joinpath(fp.stem)
        frontend = Path(OUTPUT_DIR).joinpath(f"{fp.stem}/{FRONTEND_DIR}")
        if not dirr.exists():
            dirr.mkdir()
        if not frontend.exists():
            frontend.mkdir()


class Main:
    output = Path(OUTPUT_DIR)

    backend = Base(SRC_BACKEND_IMG)
    main = Base(SRC_MAIN_IMG)
    frontend = Base(SRC_FRONTEND_IMG)

    header = ImageFont.truetype("src/Oswald-Regular.ttf", 60)
    paragraph = ImageFont.truetype("src/Oswald-Regular.ttf", 14)
    white = (255, 255, 255, 0)
    blue = (40, 101, 176, 0)
    white2 = (0, 0, 0, 0)

    def __init__(self) -> None:
        if not self.output.exists():
            self.output.mkdir()
        self.folders = [Folder(i) for i in Path(DATA_DIR).glob("*/")]

    def start(self) -> None:
        for folder in self.folders:
            self.create_backend(folder)
            self.create_main(folder)
            self.create_frontend(folder)

    def create_backend(self, obj: Folder) -> None:
        box = (
            self.backend.w // 2 - obj.backend.w // 2,
            self.backend.h // 2 - obj.backend.h // 2,
        )
        self.backend.image.paste(obj.backend.image, box)
        draw = ImageDraw.Draw(self.backend.image)
        w, h = draw.textsize(obj.text.title, self.header)
        box = (470 - w // 2, 1150 - h // 2)
        draw.text(
            box, obj.text.title, font=self.header, fill=self.blue,
        )
        self.backend.image.convert("RGB").save(
            self.output.joinpath(f"{obj.dirname}/backend{FFORMAT}")
        )
        self.backend.reset()

    def create_main(self, obj: Folder) -> None:
        box = (
            self.main.w // 2 - obj.main.w // 2,
            self.main.h // 2 - obj.main.h // 2,
        )
        self.main.image.paste(obj.main.image, box)
        draw = ImageDraw.Draw(self.main.image)

        w, h = draw.textsize("0", self.header)
        box = (112 - w // 2, 112 - h // 1.5)
        draw.text(
            box, "0", font=self.header, fill=self.white,
        )

        w, h = draw.textsize(obj.text.title, self.header)
        box = (470 - w // 2, 1150 - h // 2)
        draw.text(
            box, obj.text.title, font=self.header, fill=self.white,
        )
        self.main.image.convert("RGB").save(
            self.output.joinpath(f"{obj.dirname}/main{FFORMAT}")
        )
        self.main.reset()

    def create_frontend(self, obj: Folder):
        for i, el in enumerate(obj.frontend):
            if el.w > 710 or el.h > 590:
                el.image.thumbnail((710, 590), Image.ANTIALIAS)
                el.w = el.image.width
                el.h = el.image.height
            box = (
                (self.frontend.w - el.w) // 2,
                (self.frontend.h - el.h) // 2 - 200,
            )
            self.frontend.image.paste(el.image, box)

            draw = ImageDraw.Draw(self.frontend.image)

            # card numeration
            w, h = draw.textsize(str(i + 1), self.header)
            box = (112 - w // 2, 112 - h // 1.5)
            draw.text(box, str(i + 1), font=self.header, fill=self.white2)

            # card header
            w, h = draw.textsize(obj.text.text[i][0], self.header)
            box = (470 - w // 2, 880 - h // 2)
            draw.text(
                box, obj.text.text[i][0], font=self.header, fill=self.white2,
            )

            # card desc 1
            draw.text(
                (90, 940), obj.text.text[i][1], font=self.paragraph, fill=self.white2,
            )

            # card desc 2
            draw.text(
                (490, 940), obj.text.text[i][2], font=self.paragraph, fill=self.white2,
            )

            self.frontend.image.convert("RGB").save(
                f"{OUTPUT_DIR}/{obj.dirname}/{FRONTEND_DIR}/{i}{FFORMAT}"
            )
            self.frontend.reset()


img = Main().start()

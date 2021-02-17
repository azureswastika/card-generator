from pathlib import Path
from textwrap import fill, wrap

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

SRC_BACKEND_IMG = "src/backend.jpg"
SRC_MAIN_IMG = "src/main.jpg"
SRC_FRONTEND_IMG = "src/frontend.jpg"
OUTPUT_DIR = "output"
DATA_DIR = "static"

FONT = "src/Oswald-Regular.ttf"
FFORMAT = "png"
CONVERT = "RGB"

static = Path(DATA_DIR)
output = Path(OUTPUT_DIR)
output.mkdir(exist_ok=True)
header = ImageFont.truetype(FONT, 55)
paragraph = ImageFont.truetype(FONT, 15)
white = "white"
black = (0, 0, 0, 0)
blue = (40, 101, 176, 0)


class Base:
    def __init__(self, fp: str) -> None:
        self._image = Image.open(fp)
        self.image = self._image.copy()
        self.w, self.h = self.image.size

    def reset(self) -> None:
        self.image = self._image.copy()


class ImageDescriptor:
    def __set__(self, obj, image):
        if image.width > 710 or image.height > 590:
            image.thumbnail((710, 590), Image.ANTIALIAS)
        obj.__dict__[self.name] = image

    def __set_name__(self, owner, name):
        self.name = name


class Geneartor:
    f_backend = ImageDescriptor()
    f_main = ImageDescriptor()

    backend = Base(SRC_BACKEND_IMG)
    main = Base(SRC_MAIN_IMG)
    frontend = Base(SRC_FRONTEND_IMG)

    output_files = list()

    def __init__(self, obj) -> None:
        self.name = obj.name
        output.joinpath(self.name).mkdir(exist_ok=True)
        output.joinpath(self.name, "frontend").mkdir(exist_ok=True)
        self.title = self.process_text(obj.backend.title)
        self.f_backend = Image.open(static.joinpath(obj.backend.backend))
        self.f_main = Image.open(static.joinpath(obj.backend.main))
        self.cards = obj.cards

    def start(self) -> None:
        self.create_backend()
        self.create_frontend()
        self.create_main()
        self.create_pdf()

    def create_backend(self) -> None:
        box = (
            (self.backend.w - self.f_backend.width) // 2,
            (self.backend.h - self.f_backend.height) // 2,
        )
        self.backend.image.paste(self.f_backend, box, self.f_backend.convert("RGBA"))
        draw = ImageDraw.Draw(self.backend.image)
        draw = self.add_title(draw, self.title, blue, 1150)
        self.backend.image.convert(CONVERT).save(
            output.joinpath(f"{self.name}/backend.{FFORMAT}")
        )
        self.backend_path = output.joinpath(f"{self.name}/backend.{FFORMAT}")
        self.backend.reset()

    def create_main(self) -> None:
        box = (
            self.main.w // 2 - self.f_main.width // 2,
            self.main.h // 2 - self.f_main.height // 2,
        )
        self.main.image.paste(self.f_main, box, self.f_main.convert("RGBA"))
        draw = ImageDraw.Draw(self.main.image)
        w, h = draw.textsize("0", header)
        box = (112 - w // 2, 112 - h // 1.5)
        draw.text(
            box, "0", font=header, fill=white,
        )
        self.main.image.convert(CONVERT).save(
            output.joinpath(f"{self.name}/main.{FFORMAT}")
        )
        self.output_files.append(str(output.joinpath(f"{self.name}/main.{FFORMAT}")))
        self.main.reset()

    def create_frontend(self):
        for el in self.cards:
            image = Image.open(static.joinpath(el.image))
            if image.width > 710 or image.height > 590:
                image.thumbnail((710, 590), Image.ANTIALIAS)
            box = (
                (self.frontend.w - image.width) // 2,
                (self.frontend.h - image.height) // 2 - 200,
            )
            self.frontend.image.paste(image, box, image.convert("RGBA"))
            draw = ImageDraw.Draw(self.frontend.image)
            w, h = draw.textsize(str(el.num), header)
            box = (112 - w // 2, 112 - h // 1.5)
            draw.text(box, str(el.num), font=header, fill=black)
            title = self.process_text(el.title)
            draw = self.add_title(draw, title, black)
            draw.multiline_text(
                (90, 960), fill(el.block1, 58), font=paragraph, fill=black,
            )
            draw.multiline_text(
                (490, 960), fill(el.block2, 58), font=paragraph, fill=black,
            )
            self.frontend.image.convert(CONVERT).save(
                f"{OUTPUT_DIR}/{self.name}/frontend/{el.num}.{FFORMAT}"
            )
            self.output_files.append(f"{OUTPUT_DIR}/{self.name}/frontend/{el.num}.{FFORMAT}")
            self.frontend.reset()

    def add_title(self, draw, title, fill, heigth=None):
        if list(title).count("\n") >= 2:
            n_count = list(title).count("\n")
            title = self.process_text(title, 35 + 5 * n_count)
            subheader = ImageFont.truetype(FONT, 55 - 5 * n_count)
            w, h = draw.textsize(title, subheader)
            box = self.process_heigth(w, h, heigth)
            draw.multiline_text(box, title, font=subheader, fill=fill, align="center")
            return draw
        w, h = draw.textsize(title, header)
        box = self.process_heigth(w, h, heigth)
        draw.multiline_text(
            box, title, font=header, fill=fill, align="center",
        )
        return draw

    def create_pdf(self, step=3):
        # FIXME
        pdf = canvas.Canvas(f"{OUTPUT_DIR}/{self.name}/pdf_file.pdf")
        pdf.setPageSize((2480, 3508))
        for i in range(0, len(self.output_files), step):
            images = self.output_files[i:i + step]
        pdf.save()
        self.output_files = list()

    def process_heigth(self, w, h, heigth):
        if heigth:
            return ((self.frontend.w - w) / 2, heigth - h / 2)
        return ((self.frontend.w - w) / 2, (self.frontend.h - h) / 2 + 150)

    @staticmethod
    def process_text(text, width=35):
        return "\n".join(line for line in wrap(text, width))

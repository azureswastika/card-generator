from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField
from wtforms.fields.core import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, NumberRange

style = {"class": "form-control"}
images = UploadSet("images", IMAGES, "media")


class FormBase(FlaskForm):
    def get_data(self):
        return dict([(field, self._fields.get(field).data) for field in self._fields])

    def load_data(self, obj):
        for field in self._fields:
            self._fields[field].data = obj.__dict__["__data__"][field]


class CreateProject(FormBase):
    name = StringField("Название проекта", validators=[DataRequired()], render_kw=style)


class AddBackendProject(FormBase):
    title = StringField("Заголовок", validators=[DataRequired()], render_kw=style)
    backend = FileField(
        "Оборотная сторона", validators=[FileAllowed(images)], render_kw=style
    )
    main = FileField(
        "Нулевая страница", validators=[FileAllowed(images)], render_kw=style
    )


class AddCardProject(FormBase):
    title = StringField("Заголовок", validators=[DataRequired()], render_kw=style)
    image = FileField(
        "Фото", validators=[FileRequired(), FileAllowed(images)], render_kw=style
    )
    block1 = TextAreaField(label="Блок текста 1", render_kw=style)
    block2 = TextAreaField(label="Блок текста 2", render_kw=style)


class UpdateCardProject(FormBase):
    num = IntegerField("Нумерация", [NumberRange(min=1)], render_kw=style)
    title = StringField("Заголовок", validators=[DataRequired()], render_kw=style)
    image = FileField("Фото", validators=[FileAllowed(images)], render_kw=style)
    block1 = TextAreaField(label="Блок текста 1", render_kw=style)
    block2 = TextAreaField(label="Блок текста 2", render_kw=style)

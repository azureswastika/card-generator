from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired

style = {"class": "form-control"}
images = UploadSet("images", IMAGES, "media")


class CreateProject(FlaskForm):
    name = StringField("Название проекта", validators=[DataRequired()], render_kw=style)


class AddBackendProject(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()], render_kw=style)
    backend = FileField("Backend", validators=[FileAllowed(images)], render_kw=style)
    main = FileField("Main", validators=[FileAllowed(images)], render_kw=style)


class AddCardProject(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()], render_kw=style)
    image = FileField("Фото", validators=[FileAllowed(images)], render_kw=style)
    block1 = TextAreaField(label="Блок текста 1", render_kw=style)
    block2 = TextAreaField(label="Блок текста 2", render_kw=style)

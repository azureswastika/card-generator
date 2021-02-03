from flask_uploads import IMAGES, UploadSet
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField
from wtforms.validators import DataRequired

style = {"class": "form-control"}
images = UploadSet("images", IMAGES, "media")


class CreateProject(FlaskForm):
    name = StringField("Название проекта", validators=[DataRequired()], render_kw=style)


class AddBackendProject(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()], render_kw=style)
    image = FileField("Фото", validators=[FileAllowed(images)])

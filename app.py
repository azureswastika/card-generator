from pathlib import Path

from flask import Flask, redirect, render_template, request
from flask.helpers import url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads
from peewee import IntegrityError
from werkzeug.utils import secure_filename

from database import Project, ProjectBackend
from forms import AddBackendProject, CreateProject

upload_dir = Path(__file__).parent.joinpath("static")
upload_dir.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["WTF_CSRF_ENABLED"] = False

app.config["UPLOADED_IMAGES_DEST"] = upload_dir
images = UploadSet("images", IMAGES, "static")
configure_uploads(app, (images,))


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def root():
    form = CreateProject()
    if request.method == "POST":
        if form.validate_on_submit():
            project_name = form.name.data
            try:
                Project.create(name=project_name).save()
            except IntegrityError:
                pass
            project = Project.get(name=project_name)
            return redirect(url_for("project", pk=project.id))
    projects = Project.select()
    context = {"projects": projects, "form": form}
    return render_template("index.html", **context)


@app.route("/project/<int:pk>", methods=["GET", "POST"])
def project(pk):
    obj = Project.get_or_none(id=pk)
    obj.backend()
    if not obj:
        return redirect(url_for("root"))
    backend_form = AddBackendProject()
    if request.method == "POST":
        if backend_form.validate_on_submit():
            project_title = backend_form.title.data
            image = request.files["image"]
            path = upload_dir.joinpath(secure_filename(image.filename))
            if image:
                image.save(path)
            elif obj.backend:
                path = obj.backend.image
            if obj.backend:
                obj.backend.title = project_title
                obj.backend.image = path.name
                obj.backend.save()
            else:
                ProjectBackend.create(project=obj, title=project_title, image=path)
            return redirect(url_for("project", pk=obj.id))
    if obj.backend:
        backend_form.title.data = obj.backend.title
        print(obj.backend.image)
    context = {"project": obj, "backend_form": backend_form}
    return render_template("project.html", **context)


@app.route("/project/<int:pk>/delete", methods=["GET"])
def delete_project(pk):
    Project.get_or_none(id=pk).dlt()
    return redirect(url_for("root"))


if __name__ == "__main__":
    app.run("localhost", 8000, True)

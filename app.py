from pathlib import Path
from shutil import rmtree

from flask import Flask, redirect, render_template, request
from flask.helpers import url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads
from peewee import IntegrityError
from werkzeug.utils import secure_filename

from database import Project, ProjectBackend
from forms import AddBackendProject, AddCardProject, CreateProject

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
            upload_dir.joinpath(project_name).mkdir(exist_ok=True)
            return redirect(url_for("project", pk=project.id))
    projects = Project.select()
    context = {"projects": projects, "form": form}
    return render_template("index.html", **context)


@app.route("/project/<int:pk>", methods=["GET", "POST"])
def project(pk):
    obj = Project.get_or_none(id=pk)
    if not obj:
        return redirect(url_for("root"))
    obj.backend()
    backend_form = AddBackendProject()
    if request.method == "POST":
        if backend_form.validate_on_submit():
            project_title = backend_form.title.data
            backend = request.files["backend"]
            main = request.files["main"]
            b_path = upload_dir.joinpath(obj.name, secure_filename(backend.filename))
            m_path = upload_dir.joinpath(obj.name, secure_filename(main.filename))
            if backend:
                try:
                    upload_dir.joinpath(obj.backend.backend).unlink(missing_ok=True)
                except AttributeError:
                    pass
                backend.save(b_path)
            elif obj.backend:
                b_path = Path(obj.backend.backend)
            if main:
                try:
                    upload_dir.joinpath(obj.backend.main).unlink(missing_ok=True)
                except AttributeError:
                    pass
                backend.save(m_path)
            elif obj.main:
                m_path = Path(obj.backend.main)
            if obj.backend:
                obj.backend.title = project_title
                obj.backend.backend = f"{obj.name}/{b_path.name}"
                obj.backend.main = f"{obj.name}/{m_path.name}"
                obj.backend.save()
            else:
                ProjectBackend.create(project=obj, title=project_title, backend=b_path, main=m_path)
            return redirect(url_for("project", pk=obj.id))
    if obj.backend:
        backend_form.title.data = obj.backend.title

    # card form
    card_form = AddCardProject()
    if request.method == "POST":
        if card_form.validate_on_submit():
            card_title = card_form.title.data
            image = request.files["image"]
    context = {"project": obj, "backend_form": backend_form, "card_form": card_form}
    return render_template("project.html", **context)


@app.route("/project/<int:pk>/delete", methods=["GET"])
def delete_project(pk):
    project = Project.get_or_none(id=pk)
    rmtree(upload_dir.joinpath(project.name), ignore_errors=True)
    project.dlt()
    return redirect(url_for("root"))


if __name__ == "__main__":
    app.run("localhost", 8000, True)

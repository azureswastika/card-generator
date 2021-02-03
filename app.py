from pathlib import Path
from random import choices
from shutil import rmtree
from string import ascii_letters

from flask import Flask, redirect, render_template, request
from flask.helpers import url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads
from peewee import IntegrityError
from werkzeug.utils import secure_filename

from database import Project, ProjectBackend, ProjectCard
from forms import AddBackendProject, AddCardProject, CreateProject
from main import Geneartor

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
                main.save(m_path)
            elif obj.backend:
                m_path = Path(obj.backend.main)
            if obj.backend:
                obj.backend.title = project_title
                obj.backend.backend = f"{obj.name}/{b_path.name}"
                obj.backend.main = f"{obj.name}/{m_path.name}"
                obj.backend.save()
            else:
                ProjectBackend.create(
                    project=obj,
                    title=project_title,
                    backend=f"{obj.name}/{b_path.name}",
                    main=f"{obj.name}/{m_path.name}",
                )
            return redirect(url_for("project", pk=obj.id))
    if obj.backend:
        backend_form.title.data = obj.backend.title
    context = {"project": obj, "form": backend_form}
    return render_template("project.html", **context)


@app.route("/project/<int:pk>/delete", methods=["GET"])
def delete_project(pk):
    project = Project.get_or_none(id=pk)
    rmtree(upload_dir.joinpath(project.name), ignore_errors=True)
    project.dlt()
    return redirect(url_for("root"))


@app.route("/project/<int:pk>/add_card", methods=["GET", "POST"])
def add_card(pk):
    num = 1
    obj = Project.get_or_none(id=pk)
    if not obj:
        return redirect(url_for("root"))
    obj.backend()
    card_form = AddCardProject()
    if request.method == "POST":
        if card_form.validate_on_submit():
            card_title = card_form.title.data
            block1 = card_form.block1.data
            block2 = card_form.block2.data
            image = request.files["image"]
            path = upload_dir.joinpath(obj.name, secure_filename(image.filename))
            if path.exists():
                path = upload_dir.joinpath(
                    obj.name,
                    f"{path.stem}{''.join(choices(ascii_letters))}.{path.suffix}",
                )
            if image:
                image.save(path)
            if obj.cards:
                num = obj.cards[-1].num + 1
            ProjectCard.create(
                num=num,
                project=obj,
                title=card_title,
                image=f"{obj.name}/{path.name}",
                block1=block1,
                block2=block2,
            ).save()
            return redirect(url_for("project", pk=obj.id))
    context = {"project": obj, "form": card_form}
    return render_template("add_card.html", **context)


@app.route("/project/<int:project>/<int:card>/delete", methods=["GET"])
def delete_card(project, card):
    obj = ProjectCard.get_or_none(id=card)
    if obj:
        obj.delete_instance()
    return redirect(url_for("project", pk=project))


@app.route("/project/<int:pk>/generate", methods=["GET"])
def generat_project(pk):
    obj = Project.get_by_id(pk)
    obj.backend()
    if obj and obj.backend and obj.cards:
        generator = Geneartor(obj)
        generator.start()
    return redirect(url_for("project", pk=pk))


if __name__ == "__main__":
    app.run("localhost", 8000, True)

from shutil import rmtree

from flask import Flask, redirect, render_template, request
from flask.helpers import url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads
from peewee import IntegrityError
from werkzeug.utils import secure_filename

from database import Project, ProjectBackend, ProjectCard
from forms import AddBackendProject, AddCardProject, CreateProject, UpdateCardProject
from main import Geneartor
from utlis import process_path, upload_dir

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
            if backend:
                b_path = process_path(
                    obj.name,
                    upload_dir.joinpath(obj.name, secure_filename(backend.filename)),
                )
                backend.save(b_path)
                b_path = f"{obj.name}/{b_path.name}"
            else:
                try:
                    b_path = obj.backend.backend
                except AttributeError:
                    b_path = None
            if main:
                m_path = process_path(
                    obj.name,
                    upload_dir.joinpath(obj.name, secure_filename(main.filename)),
                )
                main.save(m_path)
                m_path = f"{obj.name}/{m_path.name}"
            else:
                try:
                    m_path = obj.backend.main
                except AttributeError:
                    m_path = None
            if obj.backend:
                obj.backend.title = project_title
                obj.backend.backend = b_path
                obj.backend.main = m_path
                obj.backend.save()
            else:
                ProjectBackend.create(
                    project=obj, title=project_title, backend=b_path, main=m_path,
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
            path = process_path(
                obj.name, upload_dir.joinpath(obj.name, secure_filename(image.filename))
            )
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


@app.route("/project/<int:project>/<int:card>/update", methods=["GET", "POST"])
def update_card(project, card):
    project = Project.get_or_none(id=project)
    card = ProjectCard.get_or_none(id=card)
    if not project or not card:
        return redirect(url_for("root"))
    card_form = UpdateCardProject()
    if request.method == "POST":
        if card_form.validate_on_submit():
            card_num = card_form.num.data
            card_title = card_form.title.data
            block1 = card_form.block1.data
            block2 = card_form.block2.data
            image = request.files["image"]
            if card_num != card.num:
                second_card = ProjectCard.get_or_none(project=project, num=card_num)
                if second_card:
                    second_card.num, card.num = card.num, second_card.num
                    second_card.save()
                    card.save()
            if image:
                path = process_path(
                    project.name,
                    upload_dir.joinpath(project.name, secure_filename(image.filename)),
                )
                image.save(path)
                path = f"{project.name}/{path.name}"
                card.image = path
            card.title = card_title
            card.block1 = block1
            card.block2 = block2
            card.save()
            return redirect(url_for("project", pk=project.id))
    card_form.num.data = card.num
    card_form.title.data = card.title
    card_form.block1.data = card.block1
    card_form.block2.data = card.block2
    context = {"project": project, "card": card, "form": card_form}
    return render_template("update_card.html", **context)


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

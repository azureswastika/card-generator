import subprocess
from pathlib import Path
from shutil import rmtree
from threading import Thread

from flask import Flask, redirect, render_template, request
from flask.helpers import url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads
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
    if request.method == "POST" and form.validate_on_submit():
        form = form.get_data()
        if not Project.get_or_none(**form):
            Project.create(**form).save()
        project = Project.get(**form)
        upload_dir.joinpath(project.name).mkdir(exist_ok=True)
        return redirect(url_for("project", pk=project.id))
    projects = Project.select()
    context = {"projects": projects, "form": form}
    return render_template("index.html", **context)


@app.route("/project/<int:pk>", methods=["GET", "POST"])
def project(pk):
    obj = Project.get_or_none(id=pk)()
    if not obj:
        return redirect(url_for("root"))
    backend_form = AddBackendProject()
    if request.method == "POST" and backend_form.validate_on_submit():
        backend_form = backend_form.get_data()
        backend_form["backend"] = process_image(obj, "backend")
        backend_form["main"] = process_image(obj, "main")
        if obj.backend:
            obj.backend.update_data(obj.backend.id, backend_form)
        else:
            ProjectBackend.create(project=obj, **backend_form)
        return redirect(url_for("project", pk=obj.id))
    if obj.backend:
        backend_form.load_data(obj.backend)
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
    obj = Project.get_or_none(id=pk)()
    if not obj:
        return redirect(url_for("root"))
    card_form = AddCardProject()
    if request.method == "POST" and card_form.validate_on_submit():
        card_form = card_form.get_data()
        card_form["image"] = process_image(obj, "image")
        if obj.cards:
            num = obj.cards[-1].num + 1
        ProjectCard.create(num=num, project=obj, **card_form).save()
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
    if request.method == "POST" and card_form.validate_on_submit():
        card_form = card_form.get_data()
        card_form["image"] = process_image(project, "image", card)
        if card_form["num"] != card.num:
            second_card = ProjectCard.get_or_none(project=project, num=card_form["num"])
            if second_card:
                second_card.num, card.num = card.num, second_card.num
                second_card.save()
        card.update_data(card.id, card_form)
        return redirect(url_for("project", pk=project.id))
    card_form.load_data(card)
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
    obj = Project.get_by_id(pk)()
    if obj and obj.backend and obj.cards:
        generator = Geneartor(obj)
        Thread(target=generator.start).start()
    return redirect(url_for("project", pk=pk))


@app.route("/project/<int:pk>/open_file", methods=["GET"])
def open_file(pk):
    path = Path(__file__).parent
    project = Project.get_or_none(id=pk)
    subprocess.Popen(
        [path.joinpath(f"output/{project.name}/pdf_file.pdf").absolute()], shell=True
    )
    return redirect(url_for("root"))


def process_image(obj: Project, image: str, card: ProjectCard = None) -> str or None:
    image = request.files[image]
    if image:
        path = process_path(
            obj.name, upload_dir.joinpath(obj.name, secure_filename(image.filename)),
        )
        image.save(path)
        path = f"{obj.name}/{path.name}"
        return path
    if card:
        return card.image
    try:
        path = obj.backend.backend
    except AttributeError:
        path = None
    return path


if __name__ == "__main__":
    app.run("localhost", 8000, True)

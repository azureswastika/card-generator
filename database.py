from peewee import (
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)

db = SqliteDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = db


class Project(BaseModel):
    name = CharField(100, unique=True)

    def dlt(self):
        ProjectBackend.get_or_none(project=self).delete_instance()
        for el in ProjectCard.select().where(ProjectCard.project == self):
            el.delete_instance()
        return self.delete_instance()

    def backend(self):
        self.backend = ProjectBackend.get_or_none(project=self)
        self.cards = (
            ProjectCard.select()
            .where(ProjectCard.project == self)
            .order_by(ProjectCard.num)
        )


class ProjectBackend(BaseModel):
    project = ForeignKeyField(Project, on_delete="CASCADE", unique=True)
    title = CharField(55)
    backend = CharField(255, default=None)
    main = CharField(255, default=None)


class ProjectCard(BaseModel):
    project = ForeignKeyField(Project, on_delete="CASCADE")
    num = IntegerField()
    title = CharField(55)
    image = CharField(255)
    block1 = TextField(default="")
    block2 = TextField(default="")


tables = [cls for cls in BaseModel.__subclasses__()]
db.connect()
db.create_tables(tables)

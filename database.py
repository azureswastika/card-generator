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

    def update_data(self, id, data):
        query = self.__class__.update(**data).where(self.__class__.id == id)
        query.execute()


class Project(BaseModel):
    name = CharField(100, unique=True)

    def __call__(self, *args, **kwds):
        self.backend = ProjectBackend.get_or_none(project=self)
        self.cards = (
            ProjectCard.select()
            .where(ProjectCard.project == self)
            .order_by(ProjectCard.num)
        )
        return self

    def dlt(self):
        try:
            ProjectBackend.get(project=self).delete_instance()
        except Exception:
            pass
        for el in ProjectCard.select().where(ProjectCard.project == self):
            el.delete_instance()
        return self.delete_instance()

    def update_data(self, id, data):
        query = self.__class__.update(**data).where(self.id == id)
        query.execute()


class ProjectBackend(BaseModel):
    project = ForeignKeyField(Project, on_delete="CASCADE", unique=True)
    title = CharField(55)
    backend = CharField(255, default=None, null=True)
    main = CharField(255, default=None, null=True)


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

from enum import unique
from peewee import CharField, Model, SqliteDatabase


db = SqliteDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = db


class Project(BaseModel):
    name = CharField(unique=True)


tables = [cls.__name__ for cls in BaseModel.__subclasses__()]
db.create_tables(tables)

from peewee import Model
from .. utils.dbConnection import DBConnection

class BaseModel(Model):
    class Meta:
        database = DBConnection.getDB()
from peewee import *
from Utils.dbConnection import DBConnection

class BaseModel(Model):
    class Meta:
        database = DBConnection.getDB()
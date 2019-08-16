from peewee import *

from .dbConnection import DBConnection
from ..models.user import UserModel

class DBUtil:

    @staticmethod
    def initDB():
        DBConnection.getDB().create_tables([UserModel])

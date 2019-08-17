from peewee import SqliteDatabase
import os

class DBConnection:
    db = None

    @staticmethod
    def getDB():
        if(DBConnection.db == None):
            DBConnection.db = SqliteDatabase(os.getenv("db_name") or "telegram-bot.db")

        if DBConnection.db.is_closed():
            DBConnection.db.connect()
            
        return DBConnection.db
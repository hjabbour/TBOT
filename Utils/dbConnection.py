from peewee import SqliteDatabase
import os

class DBConnection:
    db = SqliteDatabase(os.getenv("db_name") or "telegram-bot.db")

    @staticmethod
    def getDB():
        if DBConnection.db.is_closed():
            DBConnection.db.connect()
            
        return DBConnection.db
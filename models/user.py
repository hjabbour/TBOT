from peewee import *

from models.BaseModel import BaseModel

class UserModel(BaseModel):
    telegramUserId=IntegerField(unique=True)
    firstName=CharField()
    lastName=CharField()
    userName=CharField()

from peewee import CharField,IntegerField

from . base_model import BaseModel

class UserModel(BaseModel):
    telegramUserId=IntegerField(unique=True)
    firstName=CharField()
    lastName=CharField()
    userName=CharField()

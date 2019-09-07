import unittest

import os
import sys

db_file = "telegram_bot_test.db"

#Hack =(
os.environ["db_name"] = db_file

from telegram_bot.models.user import UserModel
from telegram_bot.utils.dbutils import DBUtil
from telegram_bot.utils.dbConnection import DBConnection

class TestPeewee(unittest.TestCase):

    

    def test_1_init_db(self):
        DBUtil.initDB()

    def test_2_get_db(self):
        db = DBConnection.getDB()
        self.assertIsNotNone(db)

    def test_3_create_user_model(self):
        newUser = UserModel.create(telegramUserId = 1, firstName="Test", lastName="Last", userName="usertest")
        newUser.save()

    def test_4_user_model_get(self):
        user = UserModel.get_or_none()
        self.assertIsNotNone(user)
    
    @classmethod
    def tearDownClass(cls):
        #remove db test file
        try:
            os.remove(db_file)
        except:
            print(sys.exc_info()[0])

if __name__ == '__main__':
    unittest.main()
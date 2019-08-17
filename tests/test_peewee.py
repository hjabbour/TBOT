import unittest

from telegram_bot.models.user import UserModel

class TestPeewee(unittest.TestCase):

    def test_user_model(self):
        user = UserModel.get_or_none()
        self.assertIsNotNone(user)

if __name__ == '__main__':
    unittest.main()
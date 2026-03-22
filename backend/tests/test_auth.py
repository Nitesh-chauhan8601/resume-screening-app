import unittest

from backend.models.user import User


class AuthTests(unittest.TestCase):
    def test_password_hashing(self):
        user = User(name="Test User", email="test@example.com", role="recruiter")
        user.set_password("secret123")

        self.assertNotEqual(user.password_hash, "secret123")
        self.assertTrue(user.check_password("secret123"))
        self.assertFalse(user.check_password("wrong"))


if __name__ == "__main__":
    unittest.main()

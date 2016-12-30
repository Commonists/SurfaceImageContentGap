import unittest

from surfaceimagecontentgap.bot import SurfaceContentGapBot


class TestBot(unittest.TestCase):
    def test_login_fail(self):
        bot = SurfaceContentGapBot()
        with self.assertRaises(ValueError):
            bot.login()


if __name__ == '__main__':
    unittest.main()

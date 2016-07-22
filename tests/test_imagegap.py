"""Unit test of imagegap class."""

import unittest

from surfaceimagecontentgap import imagegap


class MockArticle(object):

    """Mock of Article."""
    def __init__(self, name="", text=""):
        self.__text__ = text
        self.name = name
    def text(self):
        return self.__text__


class Test(unittest.TestCase):

    def test_isthereanimage(self):
        article = MockArticle(name="Paris", text="<gallery></gallery>")
        self.assertTrue(imagegap.isthereanimage(article))


if __name__ == "__main__":
    unittest.main()

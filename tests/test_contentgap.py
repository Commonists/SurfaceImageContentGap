#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Unit tests."""

import unittest

from surfaceimagecontentgap import contentgap


class Test(unittest.TestCase):

    def test_init_contentgap_with_empty_collection(self):
        gap = contentgap.ContentGap([])
        self.assertEqual(gap.articles, [])

if __name__ == "__main__":
    unittest.main()

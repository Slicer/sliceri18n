import unittest
from sliceri18n import Extractor

class Test(unittest.TestCase):
  def test_extract_method(self):
    self.assertEqual(Extractor.extract("../file.py"), None)

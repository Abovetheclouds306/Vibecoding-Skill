import unittest
from percent import normalize_percent
class PercentTests(unittest.TestCase):
    def test_zero(self): self.assertEqual(normalize_percent(0),0)
    def test_hundred(self): self.assertEqual(normalize_percent(100),100)
    def test_middle(self): self.assertEqual(normalize_percent(42),42)
    def test_negative(self): self.assertRaises(ValueError,normalize_percent,-1)
    def test_above(self): self.assertRaises(ValueError,normalize_percent,101)
    def test_float(self): self.assertRaises(TypeError,normalize_percent,1.0)
    def test_bool(self): self.assertRaises(TypeError,normalize_percent,True)
    def test_string(self): self.assertRaises(TypeError,normalize_percent,"42")

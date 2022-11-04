import unittest
from ptulsconv import footage

class TestFootage(unittest.TestCase):
    def test_basic_footage(self):
        r1 = "90+0"
        f1 = footage.footage_to_seconds(r1)
        self.assertEqual(float(f1 or 0), 60.0)

    def test_feet_and_frames(self):
        r1 = "1+8"
        f1 = footage.footage_to_seconds(r1)
        self.assertEqual(float(f1 or 0), 1.0)



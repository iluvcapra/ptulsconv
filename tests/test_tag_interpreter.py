import unittest

from ptulsconv.transformations import TagInterpreter

class TestTagInterpreter(unittest.TestCase):
    def test_line(self):
        ti = TagInterpreter()
        s1 = ti.parse_tags("this is a test")
        self.assertEqual(s1['line'], "this is a test")
        self.assertEqual(s1['mode'], 'Normal')
        self.assertEqual(len(s1['tags']), 0)

        s2 = ti.parse_tags("this! IS! Me! ** Typing! 123 <> |||")
        self.assertEqual(s2['line'], "this! IS! Me! ** Typing! 123 <> |||")
        self.assertEqual(s2['mode'], 'Normal')
        self.assertEqual(len(s2['tags']), 0)

    def test_tags(self):
        ti = TagInterpreter()
        s1 = ti.parse_tags("{a=100}")
        self.assertIn('tags', s1)
        self.assertEqual(s1['tags']['a'], "100")

        s2 = ti.parse_tags("{b=This is a test} [option] $X=9")
        self.assertEqual(s2['tags']['b'], 'This is a test')
        self.assertEqual(s2['tags']['option'], 'option')
        self.assertEqual(s2['tags']['X'], "9")

    def test_modes(self):
        ti = TagInterpreter()
        s1 = ti.parse_tags("@ Monday Tuesday {a=1}")
        self.assertEqual(s1['mode'], 'Timespan')

        s2 = ti.parse_tags("Monday Tuesday {a=1}")
        self.assertEqual(s2['mode'], 'Normal')

        s3 = ti.parse_tags("&Monday Tuesday {a=1}")
        self.assertEqual(s3['mode'], 'Append')

if __name__ == '__main__':
    unittest.main()

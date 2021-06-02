import unittest

from ptulsconv.docparser.tagged_string_parser_visitor import parse_tags, TagPreModes


class TestTagInterpreter(unittest.TestCase):
    def test_line(self):
        s1 = parse_tags("this is a test")
        self.assertEqual(s1.content, "this is a test")
        self.assertEqual(s1.mode, TagPreModes.NORMAL)
        self.assertEqual(len(s1.tag_dict), 0)

        s2 = parse_tags("this! IS! Me! ** Typing! 123 <> |||")
        self.assertEqual(s2.content, "this! IS! Me! ** Typing! 123 <> |||")
        self.assertEqual(s2.mode, TagPreModes.NORMAL)
        self.assertEqual(len(s2.tag_dict), 0)

    def test_tags(self):
        s1 = parse_tags("{a=100}")
        self.assertEqual(s1.tag_dict['a'], "100")

        s2 = parse_tags("{b=This is a test} [option] $X=9")
        self.assertEqual(s2.tag_dict['b'], 'This is a test')
        self.assertEqual(s2.tag_dict['option'], 'option')
        self.assertEqual(s2.tag_dict['X'], "9")

    def test_modes(self):
        s1 = parse_tags("@ Monday Tuesday {a=1}")
        self.assertEqual(s1.mode, TagPreModes.TIMESPAN)

        s2 = parse_tags("Monday Tuesday {a=1}")
        self.assertEqual(s2.mode, TagPreModes.NORMAL)

        s3 = parse_tags("&Monday Tuesday {a=1}")
        self.assertEqual(s3.mode, TagPreModes.APPEND)


if __name__ == '__main__':
    unittest.main()

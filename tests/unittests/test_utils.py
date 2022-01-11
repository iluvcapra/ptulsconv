import unittest

from ptulsconv.docparser.tag_compiler import apply_appends


class MyTestCase(unittest.TestCase):
    def test_something(self):
        v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        expected = [1, 2, 7, 5, 6, 15, 9, 10]

        should = (lambda x, y: y % 4 == 0)
        do_combine = (lambda x, y: x + y)

        r = apply_appends(iter(v), should, do_combine)
        r1 = list(r)
        self.assertEqual(r1, expected)


if __name__ == '__main__':
    unittest.main()

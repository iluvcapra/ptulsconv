import unittest

from ptulsconv.docparser.tag_compiler import Event
from ptulsconv.docparser.adr_entity import ADRLine
from fractions import Fraction

from pprint import pprint

class TestADREntity(unittest.TestCase):
    def test_something(self):
        tags = {
            'Ver': '1.0',
            'Actor': "Bill",
            'CN': "1",
            'QN': 'J1001',
            'R': 'Noise',
            'EFF': 'EFF'
        }
        event = Event(clip_name='"This is a test." (sotto voce)',
                      track_name="Justin",
                      session_name="Test Project",
                      tags=tags,
                      start=Fraction(0, 1), finish=Fraction(1, 1))

        line = ADRLine.from_event(event)

        pprint(line.__dict__)



if __name__ == '__main__':
    unittest.main()

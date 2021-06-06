import unittest

from ptulsconv.docparser.tag_compiler import Event
from ptulsconv.docparser.adr_entity import ADRLine, make_entity
from fractions import Fraction


class TestADREntity(unittest.TestCase):
    def test_event2line(self):
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

        line = make_entity(event)

        self.assertIsInstance(line, ADRLine)
        self.assertEqual('Bill', line.actor_name)
        self.assertEqual('Justin', line.character_name)
        self.assertEqual('"This is a test." (sotto voce)', line.prompt)
        self.assertEqual('Noise', line.reason)
        self.assertEqual('J1001', line.cue_number)
        self.assertEqual(True, line.effort)
        self.assertEqual('Test Project', line.title)
        self.assertEqual('1.0', line.version)


if __name__ == '__main__':
    unittest.main()

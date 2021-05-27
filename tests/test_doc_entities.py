import unittest
from ptulsconv.docparser.doc_entity import HeaderDescriptor
from fractions import Fraction


class DocParserTestCase(unittest.TestCase):

    def test_header(self):
        header = HeaderDescriptor(session_name="Test Session",
                                  sample_rate=48000.0,
                                  bit_depth=24,
                                  start_timecode="00:59:52:00",
                                  timecode_format="30",
                                  timecode_drop_frame=False,
                                  count_audio_tracks=0,
                                  count_clips=0,
                                  count_files=0)

        self.assertEqual(header.session_name, "Test Session")
        self.assertEqual(header.convert_timecode(header.start_timecode), Fraction((59 * 60 + 52) * 30, 30))


if __name__ == '__main__':
    unittest.main()

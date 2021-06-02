import unittest
from ptulsconv.docparser import parse_document
import os.path


class TestRobinHoodDF(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Robin Hood SpottingDF.txt'

    def test_header_export_df(self):
        session = parse_document(self.path)
        self.assertEqual(session.header.timecode_drop_frame, True)

    def test_a_track(self):
        session = parse_document(self.path)

        guy_track = session.tracks[4]
        self.assertEqual(guy_track.name, 'Robin')
        self.assertEqual(guy_track.comments, '[ADR] {Actor=Errol Flynn} $CN=1')
        self.assertEqual(guy_track.user_delay_samples, 0)
        self.assertListEqual(guy_track.state, [])
        self.assertEqual(len(guy_track.clips), 10)
        self.assertEqual(guy_track.clips[5].channel, 1)
        self.assertEqual(guy_track.clips[5].event, 6)
        self.assertEqual(guy_track.clips[5].clip_name, "\"Hold there! What's his fault?\" $QN=R106")
        self.assertEqual(guy_track.clips[5].start_timecode, "01:05:30;15")
        self.assertEqual(guy_track.clips[5].finish_timecode, "01:05:32;01")
        self.assertEqual(guy_track.clips[5].duration, "00:00:01;16")
        self.assertEqual(guy_track.clips[5].timestamp, None)
        self.assertEqual(guy_track.clips[5].state, 'Unmuted')

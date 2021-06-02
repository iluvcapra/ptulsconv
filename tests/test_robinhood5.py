import unittest
from ptulsconv.docparser import parse_document
import os.path


class TestRobinHood5(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Robin Hood Spotting5.txt'

    def test_skipped_segments(self):
        session = parse_document(self.path)
        self.assertIsNone(session.files)
        self.assertIsNone(session.clips)

    def test_plugins(self):
        session = parse_document(self.path)
        self.assertEqual(len(session.plugins), 2)

    def test_stereo_track(self):
        session = parse_document(self.path)
        self.assertEqual(session.tracks[1].name, 'MX WT (Stereo)')
        self.assertEqual(len(session.tracks[1].clips), 2)
        self.assertEqual(session.tracks[1].clips[0].clip_name, 'RobinHood.1-01.L')
        self.assertEqual(session.tracks[1].clips[1].clip_name, 'RobinHood.1-01.R')

    def test_a_track(self):
        session = parse_document(self.path)

        guy_track = session.tracks[8]
        self.assertEqual(guy_track.name, 'Guy')
        self.assertEqual(guy_track.comments, '[ADR] {Actor=Basil Rathbone} $CN=5')
        self.assertEqual(guy_track.user_delay_samples, 0)
        self.assertListEqual(guy_track.state, ['Solo'])
        self.assertEqual(len(guy_track.clips), 16)
        self.assertEqual(guy_track.clips[5].channel, 1)
        self.assertEqual(guy_track.clips[5].event, 6)
        self.assertEqual(guy_track.clips[5].clip_name, "\"What's your name? You Saxon dog!\" $QN=GY106")
        self.assertEqual(guy_track.clips[5].start_timecode, "01:04:19:15.00")
        self.assertEqual(guy_track.clips[5].finish_timecode, "01:04:21:28.00")
        self.assertEqual(guy_track.clips[5].duration, "00:00:02:13.00")
        self.assertEqual(guy_track.clips[5].timestamp, "01:04:19:09.70")
        self.assertEqual(guy_track.clips[5].state, 'Unmuted')


if __name__ == '__main__':
    unittest.main()

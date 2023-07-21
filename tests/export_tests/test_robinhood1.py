import unittest
from ptulsconv.docparser import parse_document
import os.path


class TestRobinHood1(unittest.TestCase):
    path = os.path.dirname(__file__) + '/../export_cases/Robin Hood Spotting.txt'

    def test_header_export(self):
        with open(self.path,"r") as file:
            session = parse_document(file.read())

        self.assertIsNotNone(session.header)
        self.assertEqual(session.header.session_name, 'Robin Hood Spotting')
        self.assertEqual(session.header.sample_rate, 48000.0)
        self.assertEqual(session.header.bit_depth, 24)
        self.assertEqual(session.header.timecode_fps, '29.97')
        self.assertEqual(session.header.timecode_drop_frame, False)

    def test_all_sections(self):

        with open(self.path,"r") as file:
            session = parse_document(file.read())

        self.assertIsNotNone(session.header)
        self.assertIsNotNone(session.files)
        self.assertIsNotNone(session.clips)
        self.assertIsNotNone(session.plugins)
        self.assertIsNotNone(session.tracks)
        self.assertIsNotNone(session.markers)

    def test_tracks(self):

        with open(self.path,"r") as file:
            session = parse_document(file.read())

        self.assertEqual(len(session.tracks), 14)
        self.assertListEqual(["Scenes", "Robin", "Will", "Marian", "John",
                              "Guy", "Much", "Butcher", "Town Crier",
                              "Soldier 1", "Soldier 2", "Soldier 3",
                              "Priest", "Guest at Court"],
                             list(map(lambda t: t.name, session.tracks)))
        self.assertListEqual(["", "[ADR] {Actor=Errol Flynn} $CN=1",
                              "[ADR] {Actor=Patrick Knowles} $CN=2",
                              "[ADR] {Actor=Olivia DeHavilland} $CN=3",
                              "[ADR] {Actor=Claude Raines} $CN=4",
                              "[ADR] {Actor=Basil Rathbone} $CN=5",
                              "[ADR] {Actor=Herbert Mundin} $CN=6",
                              "[ADR] {Actor=George Bunny} $CN=101",
                              "[ADR] {Actor=Leonard Mundie} $CN=102",
                              "[ADR] $CN=103",
                              "[ADR] $CN=104",
                              "[ADR] $CN=105",
                              "[ADR] {Actor=Thomas R. Mills} $CN=106",
                              "[ADR] $CN=107"],
                             list(map(lambda t: t.comments, session.tracks)))

    def test_a_track(self):

        with open(self.path,"r") as file:
            session = parse_document(file.read())
        
        guy_track = session.tracks[5]
        self.assertEqual(guy_track.name, 'Guy')
        self.assertEqual(guy_track.comments, '[ADR] {Actor=Basil Rathbone} $CN=5')
        self.assertEqual(guy_track.user_delay_samples, 0)
        self.assertListEqual(guy_track.state, [])
        self.assertEqual(len(guy_track.clips), 16)
        self.assertEqual(guy_track.clips[5].channel, 1)
        self.assertEqual(guy_track.clips[5].event, 6)
        self.assertEqual(guy_track.clips[5].clip_name, "\"What's your name? You Saxon dog!\" $QN=GY106")
        self.assertEqual(guy_track.clips[5].start_timecode, "01:04:19:15")
        self.assertEqual(guy_track.clips[5].finish_timecode, "01:04:21:28")
        self.assertEqual(guy_track.clips[5].duration, "00:00:02:13")
        self.assertEqual(guy_track.clips[5].timestamp, None)
        self.assertEqual(guy_track.clips[5].state, 'Unmuted')

    def test_memory_locations(self):
        with open(self.path,"r") as file:
            session = parse_document(file.read())

        self.assertEqual(len(session.markers), 1)
        self.assertEqual(session.markers[0].number, 1)
        self.assertEqual(session.markers[0].location, "01:00:00:00")
        self.assertEqual(session.markers[0].time_reference, 0)
        self.assertEqual(session.markers[0].units, "Samples")


if __name__ == '__main__':
    unittest.main()

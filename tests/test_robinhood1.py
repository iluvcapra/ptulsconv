import unittest
import ptulsconv
import pprint
import os.path


class TestRobinHood1(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Robin Hood Spotting.txt'

    def test_header_export(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            self.assertTrue('header' in parsed.keys())
            self.assertEqual(parsed['header']['session_name'], 'Robin Hood Spotting')
            self.assertEqual(parsed['header']['sample_rate'], 48000.0)
            self.assertEqual(parsed['header']['bit_depth'], 24)
            self.assertEqual(parsed['header']['timecode_format'], 29.97)

    def test_all_sections(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            self.assertIn('header', parsed.keys())
            self.assertIn('files', parsed.keys())
            self.assertIn('clips', parsed.keys())
            self.assertIn('plugins', parsed.keys())
            self.assertIn('tracks', parsed.keys())
            self.assertIn('markers', parsed.keys())

    def test_tracks(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            self.assertEqual(len(parsed['tracks']), 14)
            self.assertListEqual(["Scenes", "Robin", "Will", "Marian", "John",
                                  "Guy", "Much", "Butcher", "Town Crier",
                                  "Soldier 1", "Soldier 2", "Soldier 3",
                                  "Priest", "Guest at Court"],
                                 list(map(lambda n: n['name'], parsed['tracks'])))
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
                                 list(map(lambda n: n['comments'], parsed['tracks'])))

    def test_a_track(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            guy_track = parsed['tracks'][5]
            self.assertEqual(guy_track['name'], 'Guy')
            self.assertEqual(guy_track['comments'], '[ADR] {Actor=Basil Rathbone} $CN=5')
            self.assertEqual(guy_track['user_delay_samples'], 0)
            self.assertListEqual(guy_track['state'], [])
            self.assertEqual(len(guy_track['clips']), 16)
            self.assertEqual(guy_track['clips'][5]['channel'], 1)
            self.assertEqual(guy_track['clips'][5]['event'], 6)
            self.assertEqual(guy_track['clips'][5]['clip_name'], "\"What's your name? You Saxon dog!\" $QN=GY106")
            self.assertEqual(guy_track['clips'][5]['start_time'], "01:04:19:15")
            self.assertEqual(guy_track['clips'][5]['end_time'], "01:04:21:28")
            self.assertEqual(guy_track['clips'][5]['duration'], "00:00:02:13")
            self.assertEqual(guy_track['clips'][5]['timestamp'], None)
            self.assertEqual(guy_track['clips'][5]['state'], 'Unmuted')

    def test_memory_locations(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            self.assertEqual(len(parsed['markers']),1)
            self.assertEqual(parsed['markers'][0]['number'], 1)
            self.assertEqual(parsed['markers'][0]['location'], "01:00:00:00")
            self.assertEqual(parsed['markers'][0]['time_reference'], 0)
            self.assertEqual(parsed['markers'][0]['units'], "Samples")



if __name__ == '__main__':
    unittest.main()

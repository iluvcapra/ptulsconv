import unittest
import ptulsconv
import os.path


class TestRobinHood5(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Robin Hood Spotting5.txt'

    def test_skipped_segments(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.PTTextVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            self.assertIsNone(parsed['files'])
            self.assertIsNone(parsed['clips'])

    def test_plugins(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.PTTextVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            self.assertEqual(len(parsed['plugins']), 2)

    def test_stereo_track(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.PTTextVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            self.assertEqual(parsed['tracks'][1]['name'], 'MX WT (Stereo)')
            self.assertEqual(len(parsed['tracks'][1]['clips']), 2)
            self.assertEqual(parsed['tracks'][1]['clips'][0]['clip_name'], 'RobinHood.1-01.L')
            self.assertEqual(parsed['tracks'][1]['clips'][1]['clip_name'], 'RobinHood.1-01.R')

    def test_a_track(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.PTTextVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            guy_track = parsed['tracks'][8]
            self.assertEqual(guy_track['name'], 'Guy')
            self.assertEqual(guy_track['comments'], '[ADR] {Actor=Basil Rathbone} $CN=5')
            self.assertEqual(guy_track['user_delay_samples'], 0)
            self.assertListEqual(guy_track['state'], ['Solo'])
            self.assertEqual(len(guy_track['clips']), 16)
            self.assertEqual(guy_track['clips'][5]['channel'], 1)
            self.assertEqual(guy_track['clips'][5]['event'], 6)
            self.assertEqual(guy_track['clips'][5]['clip_name'], "\"What's your name? You Saxon dog!\" $QN=GY106")
            self.assertEqual(guy_track['clips'][5]['start_time'], "01:04:19:15.00")
            self.assertEqual(guy_track['clips'][5]['end_time'], "01:04:21:28.00")
            self.assertEqual(guy_track['clips'][5]['duration'], "00:00:02:13.00")
            self.assertEqual(guy_track['clips'][5]['timestamp'], "01:04:19:09.70")
            self.assertEqual(guy_track['clips'][5]['state'], 'Unmuted')


if __name__ == '__main__':
    unittest.main()

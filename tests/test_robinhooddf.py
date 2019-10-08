import unittest
import ptulsconv
import os.path


class TestRobinHoodDF(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Robin Hood SpottingDF.txt'

    def test_header_export_df(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            self.assertTrue('header' in parsed.keys())
            self.assertEqual(parsed['header']['timecode_drop_frame'], True)

    def test_a_track(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            guy_track = parsed['tracks'][4]
            self.assertEqual(guy_track['name'], 'Robin')
            self.assertEqual(guy_track['comments'], '[ADR] {Actor=Errol Flynn} $CN=1')
            self.assertEqual(guy_track['user_delay_samples'], 0)
            self.assertListEqual(guy_track['state'], [])
            self.assertEqual(len(guy_track['clips']), 10)
            self.assertEqual(guy_track['clips'][5]['channel'], 1)
            self.assertEqual(guy_track['clips'][5]['event'], 6)
            self.assertEqual(guy_track['clips'][5]['clip_name'], "\"Hold there! What's his fault?\" $QN=R106")
            self.assertEqual(guy_track['clips'][5]['start_time'], "01:05:30;15")
            self.assertEqual(guy_track['clips'][5]['end_time'], "01:05:32;01")
            self.assertEqual(guy_track['clips'][5]['duration'], "00:00:01;16")
            self.assertEqual(guy_track['clips'][5]['timestamp'], None)
            self.assertEqual(guy_track['clips'][5]['state'], 'Unmuted')

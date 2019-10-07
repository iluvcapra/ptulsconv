import unittest
import ptulsconv
import os.path


class TestRobinHood6(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Robin Hood Spotting6.txt'

    def test_a_track(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)
            marian_track = parsed['tracks'][6]
            self.assertEqual(marian_track['name'], 'Marian')
            self.assertEqual(marian_track['comments'], '[ADR] {Actor=Olivia DeHavilland} $CN=3')
            self.assertEqual(marian_track['user_delay_samples'], 0)
            self.assertListEqual(marian_track['state'], ['Solo'])
            self.assertEqual(len(marian_track['clips']), 4)
            self.assertListEqual(marian_track['plugins'], ['Channel Strip (mono)', 'ReVibe II (mono/5.1)'])
            self.assertEqual(marian_track['clips'][2]['channel'], 1)
            self.assertEqual(marian_track['clips'][2]['event'], 3)
            self.assertEqual(marian_track['clips'][2]['clip_name'], "\"Isn't that reason enough for a Royal Ward who must obey her guardian?\" $QN=M103")
            self.assertEqual(marian_track['clips'][2]['start_time'], "01:08:01:11")
            self.assertEqual(marian_track['clips'][2]['end_time'], "01:08:04:24")
            self.assertEqual(marian_track['clips'][2]['duration'], "00:00:03:12")
            self.assertEqual(marian_track['clips'][2]['timestamp'], "01:08:01:11")
            self.assertEqual(marian_track['clips'][2]['state'], 'Unmuted')


if __name__ == '__main__':
    unittest.main()

import unittest
import ptulsconv
import os.path

class TaggingIntegratedTests(unittest.TestCase):

    path = os.path.dirname(__file__) + '/export_cases/Tag Tests/Tag Tests.txt'

    def test_append(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            tcxform = ptulsconv.transformations.TimecodeInterpreter()
            tagxform = ptulsconv.transformations.TagInterpreter(show_progress=False,
                                                                ignore_muted=True,
                                                                log_output=False)

            parsed = tcxform.transform(parsed)
            parsed = tagxform.transform(parsed)

            self.assertTrue(len(parsed['events']) > 2)

            self.assertEqual("Dolor sic amet the rain in spain",
                             parsed['events'][2]['PT.Clip.Name'])

            self.assertTrue("01:00:10:00", parsed['events'][2]['PT.Clip.Start'])
            self.assertTrue("01:00:25:00", parsed['events'][2]['PT.Clip.Finish'])
            self.assertTrue(240, parsed['events'][2]['PT.Clip.Start_Frames'])
            self.assertTrue(600, parsed['events'][2]['PT.Clip.Finish_Frames'])

            self.assertIn('X', parsed['events'][2].keys())
            self.assertIn('ABC', parsed['events'][2].keys())
            self.assertIn('A', parsed['events'][2].keys())
            self.assertEqual('302', parsed['events'][2]['X'])
            self.assertEqual('ABC', parsed['events'][2]['ABC'])
            self.assertEqual('1', parsed['events'][2]['A'])

    def test_successive_appends(self):
        with open(self.path, 'r') as f:
            visitor = ptulsconv.DictionaryParserVisitor()
            result = ptulsconv.protools_text_export_grammar.parse(f.read())
            parsed: dict = visitor.visit(result)

            tcxform = ptulsconv.transformations.TimecodeInterpreter()
            tagxform = ptulsconv.transformations.TagInterpreter(show_progress=False,
                                                                ignore_muted=True,
                                                                log_output=False)

            parsed = tcxform.transform(parsed)
            parsed = tagxform.transform(parsed)

            self.assertTrue(len(parsed['events']) > 3)

            self.assertEqual("A B C",
                             parsed['events'][3]['PT.Clip.Name'])

            self.assertTrue("01:00:15:00", parsed['events'][3]['PT.Clip.Start'])
            self.assertTrue("01:00:45:00", parsed['events'][3]['PT.Clip.Finish'])
            self.assertTrue(80, parsed['events'][3]['PT.Clip.Start_Frames'])
            self.assertTrue(1080, parsed['events'][3]['PT.Clip.Finish_Frames'])



if __name__ == '__main__':
    unittest.main()

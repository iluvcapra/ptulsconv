import unittest
from ptulsconv.docparser import doc_entity, doc_parser_visitor, ptuls_grammar, tag_compiler
import os.path


class TaggingIntegratedTests(unittest.TestCase):
    path = os.path.dirname(__file__) + '/export_cases/Tag Tests/Tag Tests.txt'

    def test_event_list(self):
        with open(self.path, 'r') as f:
            document_ast = ptuls_grammar.protools_text_export_grammar.parse(f.read())
            document: doc_entity.SessionDescriptor = doc_parser_visitor.DocParserVisitor().visit(document_ast)
            compiler = tag_compiler.TagCompiler()
            compiler.session = document

            events = list(compiler.compile_events())

            self.assertEqual(9, len(events))
            self.assertEqual("Clip Name", events[0].clip_name)
            self.assertEqual("Lorem ipsum", events[1].clip_name)
            self.assertEqual("Dolor sic amet the rain in spain", events[2].clip_name)
            self.assertEqual("A B C", events[3].clip_name)
            self.assertEqual("Silver Bridge", events[4].clip_name)
            self.assertEqual("Region 02", events[5].clip_name)
            self.assertEqual("Region 12", events[6].clip_name)
            self.assertEqual("Region 22", events[7].clip_name)
            self.assertEqual("Region 04", events[8].clip_name)

    def test_append(self):
        with open(self.path, 'r') as f:
            document_ast = ptuls_grammar.protools_text_export_grammar.parse(f.read())
            document: doc_entity.SessionDescriptor = doc_parser_visitor.DocParserVisitor().visit(document_ast)
            compiler = tag_compiler.TagCompiler()
            compiler.session = document

            events = list(compiler.compile_events())

            self.assertTrue(len(events) > 2)

            self.assertEqual("Dolor sic amet the rain in spain", events[2].clip_name)

            self.assertEqual(document.header.convert_timecode("01:00:10:00"), events[2].start)
            self.assertEqual(document.header.convert_timecode("01:00:25:00"), events[2].finish)

            self.assertIn('X', events[2].tags.keys())
            self.assertIn('ABC', events[2].tags.keys())
            self.assertIn('A', events[2].tags.keys())
            self.assertEqual('302', events[2].tags['X'])
            self.assertEqual('ABC', events[2].tags['ABC'])
            self.assertEqual('1', events[2].tags['A'])

    def test_successive_appends(self):
        with open(self.path, 'r') as f:
            document_ast = ptuls_grammar.protools_text_export_grammar.parse(f.read())
            document: doc_entity.SessionDescriptor = doc_parser_visitor.DocParserVisitor().visit(document_ast)
            compiler = tag_compiler.TagCompiler()
            compiler.session = document

            events = list(compiler.compile_events())

            self.assertTrue(len(events) > 3)

            self.assertEqual("A B C", events[3].clip_name)

            self.assertEqual(document.header.convert_timecode("01:00:15:00"), events[3].start)
            self.assertEqual(document.header.convert_timecode("01:00:45:00"), events[3].finish)


if __name__ == '__main__':
    unittest.main()

import ptulsconv
import json
import sys

def convert(input_file, output=sys.stdout):
    with open(input_file, 'r') as file:
        ast = ptulsconv.protools_text_export_grammar.parse(file.read())
        dict_parser = ptulsconv.DictionaryParserVisitor()
        parsed = dict_parser.visit(ast)

        tcxform = ptulsconv.transformations.TimecodeInterpreter()
        tagxform = ptulsconv.transformations.TagInterpreter()

        final = tagxform.transform( tcxform.transform(parsed) )

        json.dump(final, output)

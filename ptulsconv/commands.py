import ptulsconv
import json
import sys

def convert(input_file, convert_times, apply_session_start, output=sys.stdout):
    parsed = dict()
    with open(input_file, 'r') as file:
        ast = ptulsconv.protools_text_export_grammar.parse(file.read())
        dict_parser = ptulsconv.DictionaryParserVisitor()
        parsed = dict_parser.visit(ast)

    if convert_times:
        xform = ptulsconv.transformations.TimecodeInterpreter()
        xform.apply_session_start = apply_session_start
        parsed = xform.transform(parsed)

    json.dump(parsed, output)


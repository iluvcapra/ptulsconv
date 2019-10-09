import ptulsconv
import json
import sys

def fmp_dump(data, output):
    from xml.etree.ElementTree import TreeBuilder, ElementTree, tostring
    doc = TreeBuilder(element_factory=None)

    field_map = ((['Title', 'PT.Session.Name'], 'Title', str),
                 (['Supv'], 'Supervisor', str),
                 (['Client'], 'Client', str),
                 (['Sc'], 'Scene', str),
                 (['Ver'], 'Version', str),
                 (['Reel'], 'Reel', str),
                 (['PT.Clip.Start'], 'Start', str),
                 (['PT.Clip.Finish'], 'Finish', str),
                 (['PT.Clip.Start_Frames'], 'Start Frames', int),
                 (['PT.Clip.Finish_Frames'], 'Finish Frames', int),
                 (['P'], 'Priority', int),
                 (['QN'], 'Cue Number', str),
                 (['Char', 'PT.Track.Name'], 'Charater Name', str),
                 (['Actor'], 'Actor Name', str),
                 (['CN'], 'Character Number', str),
                 (['R'], 'Reason', str),
                 (['Rq'], 'Requested by', str),
                 (['Spot'], 'Spot', str),
                 (['event_name', 'Line'], 'Line', str),
                 (['Shot'], 'Shot', str),
                 (['Note'], 'Note', str),
                 (['Mins'], 'Time Budget Mins', float),
                 (['EFF'], 'Effort', str),
                 (['TV'], 'TV', str),
                 (['TBW'], 'To Be Written', str),
                 (['OMIT'], 'Omit', str),
                 (['ADLIB'], 'Adlib', str),
                 (['OPT'], 'Optional', str))

    doc.start('FMPXMLRESULT', {'xmlns': 'http://www.filemaker.com/fmpxmlresult'})

    doc.start('ERRORCODE')
    doc.data('0')
    doc.end('ERRORCODE')

    doc.start('PRODUCT', {'NAME': 'ptulsconv', 'VERSION': '0.0.1'})
    doc.end('PRODUCT')

    doc.start('DATABASE', {'DATEFORMAT': 'MM/dd/yy', 'LAYOUT':'summary', 'TIMEFORMAT':'hh:mm:ss',
                           'RECORDS': str(len(data['events'])), 'NAME': 'OUTPUT'})
    doc.end('DATABASE')

    doc.start('METADATA')
    for field in field_map:
        tp = field[2]
        ft = 'TEXT'
        if tp is int or tp is float:
            ft = 'NUMBER'

        doc.start('FIELD', {'EMPTYOK': 'YES',
                            'MAXREPEAT': '1',
                            'NAME': field[1],
                            'TYPE': ft })

        doc.end('FIELD')
    doc.end('METADATA')

    doc.start('RESULTSET', {'FOUND': str(len(data['events'])) })
    for event in data['events']:
        doc.start('ROW')
        for field in field_map:
            doc.start('COL')
            doc.start('DATA')
            for key_attempt in field[0]:
                if key_attempt in event.keys():
                    doc.data(str(event[key_attempt]))
                    break
            doc.end('DATA')
            doc.end('COL')
        doc.end('ROW')
    doc.end('RESULTSET')

    doc.end('FMPXMLRESULT')
    docelem = doc.close()
    xmlstr = tostring(docelem, encoding='unicode', method='xml')
    output.write(xmlstr)



def convert(input_file, format='fmp', start=None, end=None, output=sys.stdout):
    with open(input_file, 'r') as file:
        ast = ptulsconv.protools_text_export_grammar.parse(file.read())
        dict_parser = ptulsconv.DictionaryParserVisitor()
        raw_parsed = dict_parser.visit(ast)

        tcxform = ptulsconv.transformations.TimecodeInterpreter()
        tagxform = ptulsconv.transformations.TagInterpreter()

        parsed = tagxform.transform(tcxform.transform(raw_parsed))

        if start is not None and end is not None:

            start_fs = tcxform.convert_time(start,
                                            frame_rate=raw_parsed['header']['timecode_format'],
                                            drop_frame=raw_parsed['header']['timecode_drop_frame'])['frame_count']

            end_fs = tcxform.convert_time(end,
                                            frame_rate=raw_parsed['header']['timecode_format'],
                                            drop_frame=raw_parsed['header']['timecode_drop_frame'])['frame_count']

            subclipxform = ptulsconv.transformations.SubclipOfSequence(start=start_fs, end=end_fs)
            parsed = subclipxform.transform(parsed)

        if format == 'json':
            json.dump(parsed, output)
        elif format == 'fmp':
            fmp_dump(parsed, output)


import io
import json
import os
import os.path
import pathlib
import subprocess
import sys
from itertools import chain
from xml.etree.ElementTree import TreeBuilder, tostring

import ptulsconv
from .reporting import print_section_header_style, print_status_style, print_warning
from .validations import *

from ptulsconv.pdf.supervisor_1pg import output_report as output_supervisor_1pg
from ptulsconv.pdf.line_count import output_report as output_line_count
from ptulsconv.pdf.talent_sides import output_report as output_talent_sides
from ptulsconv.pdf.summary_log import output_report as output_summary

# field_map maps tags in the text export to fields in FMPXMLRESULT
#  - tuple field 0 is a list of tags, the first tag with contents will be used as source
#  - tuple field 1 is the field in FMPXMLRESULT
#  - tuple field 2 the constructor/type of the field
adr_field_map = ((['Title', 'PT.Session.Name'], 'Title', str),
                 (['Supv'], 'Supervisor', str),
                 (['Client'], 'Client', str),
                 (['Sc'], 'Scene', str),
                 (['Ver'], 'Version', str),
                 (['Reel'], 'Reel', str),
                 (['PT.Clip.Start'], 'Start', str),
                 (['PT.Clip.Finish'], 'Finish', str),
                 (['PT.Clip.Start_Seconds'], 'Start Seconds', float),
                 (['PT.Clip.Finish_Seconds'], 'Finish Seconds', float),
                 (['PT.Clip.Start_Frames'], 'Start Frames', int),
                 (['PT.Clip.Finish_Frames'], 'Finish Frames', int),
                 (['P'], 'Priority', int),
                 (['QN'], 'Cue Number', str),
                 (['Char', 'PT.Track.Name'], 'Character Name', str),
                 (['Actor'], 'Actor Name', str),
                 (['CN'], 'Character Number', str),
                 (['R'], 'Reason', str),
                 (['Rq'], 'Requested by', str),
                 (['Spot'], 'Spot', str),
                 (['PT.Clip.Name', 'Line'], 'Line', str),
                 (['Shot'], 'Shot', str),
                 (['Note'], 'Note', str),
                 (['Mins'], 'Time Budget Mins', float),
                 (['EFF'], 'Effort', str),
                 (['TV'], 'TV', str),
                 (['TBW'], 'To Be Written', str),
                 (['OMIT'], 'Omit', str),
                 (['ADLIB'], 'Adlib', str),
                 (['OPT'], 'Optional', str),
                 (['Movie.Filename'], 'Movie', str),
                 (['Movie.Start_Offset_Seconds'], 'Movie Seconds', float),
                 )


def normalize_record_keys(records):
    for record in records['events']:
        for field in adr_field_map:
            spot_keys = field[0]
            output_key = field[1]
            field_type = field[2]
            for attempt_key in spot_keys:
                if attempt_key in record.keys():
                    record[output_key] = field_type(record[attempt_key])

    return records


def fmp_dump(data, input_file_name, output):
    doc = TreeBuilder(element_factory=None)

    doc.start('FMPXMLRESULT', {'xmlns': 'http://www.filemaker.com/fmpxmlresult'})

    doc.start('ERRORCODE', {})
    doc.data('0')
    doc.end('ERRORCODE')

    doc.start('PRODUCT', {'NAME': ptulsconv.__name__, 'VERSION': ptulsconv.__version__})
    doc.end('PRODUCT')

    doc.start('DATABASE', {'DATEFORMAT': 'MM/dd/yy', 'LAYOUT': 'summary', 'TIMEFORMAT': 'hh:mm:ss',
                           'RECORDS': str(len(data['events'])), 'NAME': os.path.basename(input_file_name)})
    doc.end('DATABASE')

    doc.start('METADATA', {})
    for field in adr_field_map:
        tp = field[2]
        ft = 'TEXT'
        if tp is int or tp is float:
            ft = 'NUMBER'

        doc.start('FIELD', {'EMPTYOK': 'YES', 'MAXREPEAT': '1', 'NAME': field[1], 'TYPE': ft})
        doc.end('FIELD')
    doc.end('METADATA')

    doc.start('RESULTSET', {'FOUND': str(len(data['events']))})
    for event in data['events']:
        doc.start('ROW', {})
        for field in adr_field_map:
            doc.start('COL', {})
            doc.start('DATA', {})
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


import glob

xslt_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'xslt')

def xform_options():
    return glob.glob(os.path.join(xslt_path, "*.xsl"))

def dump_xform_options(output=sys.stdout):
    print("# Available transforms:", file=output)
    print("# Transform dir: %s" % (xslt_path), file=output)
    for f in xform_options():
        base = os.path.basename(f)
        name, _ = os.path.splitext(base)
        print("#    " + name, file=output)

def dump_field_map(field_map_name, output=sys.stdout):
    output.write("# Map of Tag fields to XML output columns\n")
    output.write("# (in order of precedence)\n")
    output.write("# \n")
    field_map = []
    if field_map_name == 'ADR':
        field_map = adr_field_map
        output.write("# ADR Table Fields\n")

    output.write("# \n")
    output.write("# Tag Name                    | FMPXMLRESULT Column  | Type    | Column \n")
    output.write("# ----------------------------+----------------------+---------+--------\n")

    for n, field in enumerate(field_map):
        for tag in field[0]:
            output.write("# %-27s-> %-20s | %-8s| %-7i\n" % (tag[:27], field[1][:20], field[2].__name__, n + 1))


def fmp_transformed_dump(data, input_file, xsl_name, output):
    pipe = io.StringIO()
    print_status_style("Generating base XML")
    fmp_dump(data, input_file, pipe)

    strdata = pipe.getvalue()
    print_status_style("Base XML size %i" % (len(strdata)))

    print_status_style("Running xsltproc")

    xsl_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'xslt', xsl_name + ".xsl")
    print_status_style("Using xsl: %s" % (xsl_path))
    subprocess.run(['xsltproc', xsl_path, '-'], input=strdata, text=True,
                   stdout=output, shell=False, check=True)


def convert(input_file, output_format='fmpxml', start=None, end=None, select_reel=None,
            progress=False, include_muted=False, xsl=None,
            output=sys.stdout, log_output=sys.stderr, warnings=False, spelling=False):
    with open(input_file, 'r') as file:
        print_section_header_style('Parsing')
        ast = ptulsconv.protools_text_export_grammar.parse(file.read())
        dict_parser = ptulsconv.DictionaryParserVisitor()
        parsed = dict_parser.visit(ast)

        print_status_style('Session title: %s' % parsed['header']['session_name'])
        print_status_style('Session timecode format: %f' % parsed['header']['timecode_format'])
        print_status_style('Fount %i tracks' % len(parsed['tracks']))
        print_status_style('Found %i markers' % len(parsed['markers']))

        tcxform = ptulsconv.transformations.TimecodeInterpreter()
        tagxform = ptulsconv.transformations.TagInterpreter(show_progress=progress, ignore_muted=(not include_muted),
                                                            log_output=log_output)

        parsed = tcxform.transform(parsed)
        parsed = tagxform.transform(parsed)

        if start is not None and end is not None:
            start_fs = tcxform.convert_time(start,
                                            frame_rate=parsed['header']['timecode_format'],
                                            drop_frame=parsed['header']['timecode_drop_frame'])['frame_count']

            end_fs = tcxform.convert_time(end,
                                          frame_rate=parsed['header']['timecode_format'],
                                          drop_frame=parsed['header']['timecode_drop_frame'])['frame_count']

            subclipxform = ptulsconv.transformations.SubclipOfSequence(start=start_fs, end=end_fs)
            parsed = subclipxform.transform(parsed)

        if select_reel is not None:
            reel_xform = ptulsconv.transformations.SelectReel(reel_num=select_reel)
            parsed = reel_xform.transform(parsed)


        if warnings:
            for warning in chain(validate_unique_field(parsed, field='QN'),
                                 validate_non_empty_field(parsed, field='QN'),
                                 validate_non_empty_field(parsed, field='CN'),
                                 validate_non_empty_field(parsed, field='Char'),
                                 validate_non_empty_field(parsed, field='Title'),
                                 validate_dependent_value(parsed, key_field='CN',
                                                          dependent_field='Char'),
                                 validate_dependent_value(parsed, key_field='CN',
                                                          dependent_field='Actor'),
                                 validate_unique_count(parsed, field='Title', count=1),
                                 validate_unique_count(parsed, field='Spotting', count=1),
                                 validate_unique_count(parsed, field='Supervisor', count=1)):

                print_warning(warning.report_message())

        if output_format == 'json':
            json.dump(normalize_record_keys(parsed), output)
        elif output_format == 'full':
            print("Sorry, the `full` output type is not yet supported.")
            normalized_records = normalize_record_keys(parsed)

            output_supervisor_1pg(normalized_records)
            output_talent_sides(normalized_records)
            output_line_count(normalized_records)
            output_summary(normalized_records)

        elif output_format == 'fmpxml':
            if xsl is None:
                fmp_dump(parsed, input_file, output)
            else:
                print_section_header_style("Performing XSL Translation")
                print_status_style("Using builtin translation: %s" % (xsl))
                fmp_transformed_dump(parsed, input_file, xsl, output)

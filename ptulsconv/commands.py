import json
import os

import sys
from itertools import chain

import csv

import ptulsconv
from .reporting import print_section_header_style, print_status_style, print_warning
from .validations import *
from .xml.common import fmp_dump, fmp_transformed_dump

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
                 (['DONE'], 'Done', str),
                 (['Movie.Filename'], 'Movie', str),
                 (['Movie.Start_Offset_Seconds'], 'Movie Seconds', float),
                 )

def dump_csv(events, output=sys.stdout):
    keys = set()
    for e in events:
        keys.update(e.keys())

    dump_keyed_csv(events, keys=keys, output=output)


def dump_keyed_csv(events, keys=(), output=sys.stdout):
    writer = csv.writer(output, dialect='excel')
    writer.writerow(keys)

    for event in events:
        this_row = list()
        for key in keys:
            this_row.append(event.get(key, ""))

        writer.writerow(this_row)


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


def normalize_record_keys_for_adr(records):
    for record in records['events']:
        if 'ADR' not in record.keys():
            continue

        for field in adr_field_map:
            spot_keys = field[0]
            output_key = field[1]
            field_type = field[2]
            for attempt_key in spot_keys:
                if attempt_key in record.keys():
                    record[output_key] = field_type(record[attempt_key])
                    break

    return records


def output_adr_csv(lines):
    adr_keys = ('Title', 'Cue Number', 'Character Name', 'Reel', 'Version', 'Line',
                'Start', 'Finish', 'Reason', 'Note', 'TV', 'Version')
    reels = set([ln['Reel'] for ln in lines])
    reels.add(None)
    for n in [n['Character Number'] for n in lines]:
        for reel in reels:
            these_lines = [ln for ln in lines
                           if ln['Character Number'] == n and
                           ln.get('Reel', None) == reel]

            if len(these_lines) == 0:
                continue

            outfile_name = "%s_%s_%s_%s.csv" % (these_lines[0]['Title'],
                                                n, these_lines[0]['Character Name'], reel,)

            with open(outfile_name, mode='w', newline='') as outfile:
                dump_keyed_csv(these_lines, adr_keys, outfile)


def create_adr_reports(parsed):
    lines = [e for e in parsed['events'] if 'ADR' in e.keys()]

    print_section_header_style("Creating PDF Reports")
    print_status_style("Creating ADR Report")
    output_summary(lines)

    print_status_style("Creating Line Count")
    output_line_count(lines)

    print_status_style("Creating Supervisor Logs directory and reports")
    os.makedirs("Supervisor Logs", exist_ok=True)
    os.chdir("Supervisor Logs")
    output_supervisor_1pg(lines)
    os.chdir("..")

    print_status_style("Creating Director's Logs director and reports")
    os.makedirs("Director Logs", exist_ok=True)
    os.chdir("Director Logs")
    output_summary(lines, by_character=True)
    os.chdir("..")

    print_status_style("Creating CSV outputs")
    os.makedirs("CSV", exist_ok=True)
    os.chdir("CSV")
    output_adr_csv(lines)
    os.chdir("..")

    print_status_style("Creating Scripts directory and reports")
    os.makedirs("Talent Scripts", exist_ok=True)
    os.chdir("Talent Scripts")
    output_talent_sides(lines)


def convert(input_file, output_format='fmpxml',
            progress=False, include_muted=False, xsl=None,
            output=sys.stdout, log_output=sys.stderr, warnings=True):

    with open(input_file, 'r') as file:
        print_section_header_style('Parsing')
        parsed = parse_text_export(file)

        tcxform = ptulsconv.transformations.TimecodeInterpreter()
        tagxform = ptulsconv.transformations.TagInterpreter(show_progress=progress,
                                                            ignore_muted=(not include_muted),
                                                            log_output=log_output)

        parsed = tcxform.transform(parsed)
        parsed = tagxform.transform(parsed)

        # start=None, end=None, select_reel=None
        #
        # if start is not None and end is not None:
        #     start_fs = tcxform.convert_time(start,
        #                                     frame_rate=parsed['header']['timecode_format'],
        #                                     drop_frame=parsed['header']['timecode_drop_frame'])['frame_count']
        #
        #     end_fs = tcxform.convert_time(end,
        #                                   frame_rate=parsed['header']['timecode_format'],
        #                                   drop_frame=parsed['header']['timecode_drop_frame'])['frame_count']
        #
        #     subclipxform = ptulsconv.transformations.SubclipOfSequence(start=start_fs, end=end_fs)
        #     parsed = subclipxform.transform(parsed)
        #
        # if select_reel is not None:
        #     reel_xform = ptulsconv.transformations.SelectReel(reel_num=select_reel)
        #     parsed = reel_xform.transform(parsed)

        parsed = normalize_record_keys_for_adr(parsed)

        if warnings:
            for warning in chain(validate_unique_field(parsed, field='QN'),
                                 validate_non_empty_field(parsed, field='QN'),
                                 validate_non_empty_field(parsed, field='CN'),
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
            json.dump(parsed, output)

        elif output_format == 'csv':
            dump_csv(parsed['events'])

        elif output_format == 'adr':
            create_adr_reports(parsed)

        elif output_format == 'fmpxml':
            if xsl is None:
                fmp_dump(parsed, input_file, output, adr_field_map)
            else:
                print_section_header_style("Performing XSL Translation")
                print_status_style("Using builtin translation: %s" % xsl)
                fmp_transformed_dump(parsed, input_file, xsl, output)


def parse_text_export(file):
    ast = ptulsconv.protools_text_export_grammar.parse(file.read())
    dict_parser = ptulsconv.DictionaryParserVisitor()
    parsed = dict_parser.visit(ast)
    print_status_style('Session title: %s' % parsed['header']['session_name'])
    print_status_style('Session timecode format: %f' % parsed['header']['timecode_format'])
    print_status_style('Fount %i tracks' % len(parsed['tracks']))
    print_status_style('Found %i markers' % len(parsed['markers']))
    return parsed



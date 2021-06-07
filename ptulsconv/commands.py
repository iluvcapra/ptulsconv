import datetime
import os

import sys
from itertools import chain
import csv
from typing import List

from .docparser.adr_entity import make_entities
from .reporting import print_section_header_style, print_status_style, print_warning
from .validations import *

from ptulsconv.docparser import parse_document
from ptulsconv.docparser.tag_compiler import TagCompiler
from ptulsconv.broadcast_timecode import TimecodeFormat
from fractions import Fraction

from ptulsconv.pdf.supervisor_1pg import output_report as output_supervisor_1pg
from ptulsconv.pdf.line_count import output_report as output_line_count
from ptulsconv.pdf.talent_sides import output_report as output_talent_sides
from ptulsconv.pdf.summary_log import output_report as output_summary
from ptulsconv.pdf.continuity import output_report as output_continuity

from json import JSONEncoder


class MyEncoder(JSONEncoder):
    force_denominator: Optional[int]

    def default(self, o):
        if isinstance(o, Fraction):
            return dict(numerator=o.numerator, denominator=o.denominator)
        else:
            return o.__dict__


def output_adr_csv(lines: List[ADRLine], time_format: TimecodeFormat):
    reels = set([ln.reel for ln in lines])

    for n, name in [(n.character_id, n.character_name) for n in lines]:
        dir_name = "%s_%s" % (n, name)
        os.makedirs(dir_name, exist_ok=True)
        os.chdir(dir_name)
        for reel in reels:
            these_lines = [ln for ln in lines if ln.character_id == n and ln.reel == reel]

            if len(these_lines) == 0:
                continue

            outfile_name = "%s_%s_%s_%s.csv" % (these_lines[0].title, n, these_lines[0].character_name, reel,)

            with open(outfile_name, mode='w', newline='') as outfile:
                writer = csv.writer(outfile, dialect='excel')
                writer.writerow(['Title', 'Character Name', 'Cue Number',
                                 'Reel', 'Version',
                                 'Start', 'Finish',
                                 'Start Seconds', 'Finish Seconds',
                                 'Prompt',
                                 'Reason', 'Note', 'TV'])

                for event in these_lines:
                    this_row = [event.title, event.character_name, event.cue_number,
                                event.reel, event.version,
                                time_format.seconds_to_smpte(event.start), time_format.seconds_to_smpte(event.finish),
                                float(event.start), float(event.finish),
                                event.prompt,
                                event.reason, event.note, "TV" if event.tv else ""]

                    writer.writerow(this_row)
        os.chdir("..")

#
# def output_avid_markers(lines):
#     reels = set([ln['Reel'] for ln in lines if 'Reel' in ln.keys()])
#
#     for reel in reels:
#         pass


def create_adr_reports(lines: List[ADRLine], tc_display_format: TimecodeFormat, reel_list):

    print_status_style("Creating ADR Report")
    output_summary(lines, tc_display_format=tc_display_format)

    print_status_style("Creating Line Count")
    output_line_count(lines, reel_list=reel_list)

    print_status_style("Creating Supervisor Logs directory and reports")
    os.makedirs("Supervisor Logs", exist_ok=True)
    os.chdir("Supervisor Logs")
    output_supervisor_1pg(lines, tc_display_format=tc_display_format)
    os.chdir("..")

    print_status_style("Creating Director's Logs director and reports")
    os.makedirs("Director Logs", exist_ok=True)
    os.chdir("Director Logs")
    output_summary(lines, tc_display_format=tc_display_format, by_character=True)
    os.chdir("..")

    print_status_style("Creating CSV outputs")
    os.makedirs("CSV", exist_ok=True)
    os.chdir("CSV")
    output_adr_csv(lines, time_format=tc_display_format)
    os.chdir("..")

    # print_status_style("Creating Avid Marker XML files")
    # os.makedirs("Avid Markers", exist_ok=True)
    # os.chdir("Avid Markers")
    # output_avid_markers(lines)
    # os.chdir("..")

    print_status_style("Creating Scripts directory and reports")
    os.makedirs("Talent Scripts", exist_ok=True)
    os.chdir("Talent Scripts")
    output_talent_sides(lines, tc_display_format=tc_display_format)


# def parse_text_export(file):
#     ast = ptulsconv.protools_text_export_grammar.parse(file.read())
#     dict_parser = ptulsconv.DictionaryParserVisitor()
#     parsed = dict_parser.visit(ast)
#     print_status_style('Session title: %s' % parsed['header']['session_name'])
#     print_status_style('Session timecode format: %f' % parsed['header']['timecode_format'])
#     print_status_style('Fount %i tracks' % len(parsed['tracks']))
#     print_status_style('Found %i markers' % len(parsed['markers']))
#     return parsed


def convert(input_file, major_mode='fmpxml', output=sys.stdout, warnings=True):

    session = parse_document(input_file)
    session_tc_format = session.header.timecode_format

    if major_mode == 'raw':
        output.write(MyEncoder().encode(session))

    else:
        compiler = TagCompiler()
        compiler.session = session
        compiled_events = list(compiler.compile_events())

        if major_mode == 'tagged':
            output.write(MyEncoder().encode(compiled_events))

        else:
            generic_events, adr_lines = make_entities(compiled_events)

            # TODO: Breakdown by titles
            titles = set([x.title for x in (generic_events + adr_lines)])
            assert len(titles) == 1, "Multiple titles per export is not supported"

            print(titles)

            if warnings:
                perform_adr_validations(adr_lines)

            if major_mode == 'doc':
                print_section_header_style("Creating PDF Reports")
                report_date = datetime.datetime.now()
                reports_dir = "%s_%s" % (list(titles)[0], report_date.strftime("%Y-%m-%d_%H%M%S"))
                os.makedirs(reports_dir, exist_ok=False)
                os.chdir(reports_dir)

                scenes = sorted([s for s in compiler.compile_all_time_spans() if s[0] == 'Sc'],
                                key=lambda x: x[2])

                output_continuity(scenes=scenes, tc_display_format=session_tc_format,
                                  title=list(titles)[0], client="", supervisor="")

                # reels = sorted([r for r in compiler.compile_all_time_spans() if r[0] == 'Reel'],
                #                key=lambda x: x[2])
                reels = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']

                create_adr_reports(adr_lines,
                                   tc_display_format=session_tc_format,
                                   reel_list=sorted(reels))


def perform_adr_validations(lines):
    for warning in chain(validate_unique_field(lines,
                                               field='cue_number',
                                               scope='title'),
                         validate_non_empty_field(lines,
                                                  field='cue_number'),
                         validate_non_empty_field(lines,
                                                  field='character_id'),
                         validate_non_empty_field(lines,
                                                  field='title'),
                         validate_dependent_value(lines,
                                                  key_field='character_id',
                                                  dependent_field='character_name'),
                         validate_dependent_value(lines,
                                                  key_field='character_id',
                                                  dependent_field='actor_name')):
        print_warning(warning.report_message())


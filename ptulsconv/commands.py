"""
This module provides the main input document parsing and transform
implementation.
"""
import datetime
import os

import sys
from itertools import chain
import csv
from typing import List, Optional, Iterator
from fractions import Fraction

import ptsl

from .docparser.adr_entity import make_entities, ADRLine
from .reporting import print_section_header_style, print_status_style,\
    print_warning
from .validations import validate_unique_field, validate_non_empty_field,\
    validate_dependent_value

from ptulsconv.docparser import parse_document
from ptulsconv.docparser.tag_compiler import TagCompiler
from ptulsconv.broadcast_timecode import TimecodeFormat

from ptulsconv.pdf.supervisor_1pg import output_report as output_supervisor_1pg
from ptulsconv.pdf.line_count import output_report as output_line_count
from ptulsconv.pdf.talent_sides import output_report as output_talent_sides
from ptulsconv.pdf.summary_log import output_report as output_summary
from ptulsconv.pdf.continuity import output_report as output_continuity

from json import JSONEncoder


class MyEncoder(JSONEncoder):
    """
    A subclass of :class:`JSONEncoder` which encodes :class:`Fraction` objects
    as a dict.
    """
    force_denominator: Optional[int]

    def default(self, o):
        """

        """
        if isinstance(o, Fraction):
            return dict(numerator=o.numerator, denominator=o.denominator)
        else:
            return o.__dict__


def output_adr_csv(lines: List[ADRLine], time_format: TimecodeFormat):
    """
    Writes ADR lines as CSV to the current working directory. Creates
    directories for each character number and name pair, and within that
    directory, creates a CSV file for each reel.
    """
    reels = set([ln.reel for ln in lines])

    for n, name in [(n.character_id, n.character_name) for n in lines]:
        dir_name = "%s_%s" % (n, name)
        os.makedirs(dir_name, exist_ok=True)
        os.chdir(dir_name)
        for reel in reels:
            these_lines = [ln for ln in lines
                           if ln.character_id == n and ln.reel == reel]

            if len(these_lines) == 0:
                continue

            outfile_name = "%s_%s_%s_%s.csv" % (these_lines[0].title, n,
                                                these_lines[0].character_name,
                                                reel,)

            with open(outfile_name, mode='w', newline='') as outfile:
                writer = csv.writer(outfile, dialect='excel')
                writer.writerow(['Title', 'Character Name', 'Cue Number',
                                 'Reel', 'Version',
                                 'Start', 'Finish',
                                 'Start Seconds', 'Finish Seconds',
                                 'Prompt',
                                 'Reason', 'Note', 'TV'])

                for event in these_lines:
                    this_start = event.start or 0
                    this_finish = event.finish or 0
                    this_row = [event.title, event.character_name,
                                event.cue_number, event.reel, event.version,
                                time_format.seconds_to_smpte(this_start),
                                time_format.seconds_to_smpte(this_finish),
                                float(this_start), float(this_finish),
                                event.prompt,
                                event.reason, event.note, "TV"
                                if event.tv else ""]

                    writer.writerow(this_row)
        os.chdir("..")


def generate_documents(session_tc_format, scenes, adr_lines: Iterator[ADRLine],
                       title):
    """
    Create PDF output.
    """
    print_section_header_style("Creating PDF Reports")
    report_date = datetime.datetime.now()
    reports_dir = "%s_%s" % (title, report_date.strftime("%Y-%m-%d_%H%M%S"))
    os.makedirs(reports_dir, exist_ok=False)
    os.chdir(reports_dir)

    client = next((x.client for x in adr_lines), "")
    supervisor = next((x.supervisor for x in adr_lines), "")

    output_continuity(scenes=scenes, tc_display_format=session_tc_format,
                      title=title, client=client,
                      supervisor=supervisor)

    reels = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']

    if len(adr_lines) == 0:
        print_status_style("No ADR lines were found in the input document. "
                           "ADR reports will not be generated.")

    else:
        create_adr_reports(adr_lines, tc_display_format=session_tc_format,
                           reel_list=sorted(reels))


def create_adr_reports(lines: List[ADRLine], tc_display_format: TimecodeFormat,
                       reel_list: List[str]):
    """
    Creates a directory heirarchy and a respective set of ADR reports,
    given a list of lines.
    """

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
    output_summary(lines, tc_display_format=tc_display_format,
                   by_character=True)
    os.chdir("..")

    print_status_style("Creating CSV outputs")
    os.makedirs("CSV", exist_ok=True)
    os.chdir("CSV")
    output_adr_csv(lines, time_format=tc_display_format)
    os.chdir("..")

    print_status_style("Creating Scripts directory and reports")
    os.makedirs("Talent Scripts", exist_ok=True)
    os.chdir("Talent Scripts")
    output_talent_sides(lines, tc_display_format=tc_display_format)


def convert(major_mode, input_file=None, output=sys.stdout, warnings=True):
    """
    Primary worker function, accepts the input file and decides
    what to do with it based on the `major_mode`.

    :param input_file: a path to the input file.
    :param major_mode: the selected output mode, 'raw', 'tagged' or 'doc'.
    """
    session_text = ""
    if input_file is not None:
        with open(input_file, "r") as file:
            session_text = file.read()
    else:
        with ptsl.open_engine(
                company_name="The ptulsconv developers",
                application_name="ptulsconv") as engine:
            req = engine.export_session_as_text()
            req.utf8_encoding()
            req.include_track_edls()
            req.include_markers()
            req.time_type("tc")
            req.dont_show_crossfades()
            req.selected_tracks_only()
            session_text = req.export_string()

    session = parse_document(session_text)
    session_tc_format = session.header.timecode_format

    if major_mode == 'raw':
        output.write(MyEncoder().encode(session))

    else:
        compiler = TagCompiler()
        compiler.session = session
        compiled_events = list(compiler.compile_events())

        if major_mode == 'tagged':
            output.write(MyEncoder().encode(compiled_events))

        elif major_mode == 'doc':
            generic_events, adr_lines = make_entities(compiled_events)

            scenes = sorted([s for s in compiler.compile_all_time_spans()
                             if s[0] == 'Sc'],
                            key=lambda x: x[2])

            # TODO: Breakdown by titles
            titles = set([x.title for x in (generic_events + adr_lines)])
            if len(titles) != 1:
                print_warning("Multiple titles per export is not supported, "
                              "found multiple titles: %s Exiting." % titles)
                exit(-1)

            title = list(titles)[0]

            print_status_style(
                "%i generic events found." % len(generic_events)
            )
            print_status_style("%i ADR events found." % len(adr_lines))

            if warnings:
                perform_adr_validations(adr_lines)

            generate_documents(session_tc_format, scenes, adr_lines, title)


def perform_adr_validations(lines: Iterator[ADRLine]):
    """
    Performs validations on the input.
    """
    for warning in chain(
            validate_unique_field(lines,
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

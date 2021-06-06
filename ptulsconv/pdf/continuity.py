from fractions import Fraction
from typing import Tuple, List

from reportlab.lib.pagesizes import portrait, letter
from reportlab.lib.units import inch

from ptulsconv.broadcast_timecode import TimecodeFormat
from ptulsconv.pdf import make_doc_template

# TODO: A Continuity

def output_report(scenes: List[Tuple[str, Fraction, Fraction]],
                  tc_display_format: TimecodeFormat, title: str,
                  page_size=portrait(letter)):

        filename = "%s Continuity" % title
        document_header = "Continuity"

        doc = make_doc_template(page_size=page_size,
                                filename=filename, document_title=title,
                                title="",
                                client="",
                                document_date="",
                                supervisor="",
                                document_header=document_header,
                                left_margin=0.75 * inch)

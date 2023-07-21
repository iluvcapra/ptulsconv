# -*- coding: utf-8 -*-
from typing import List

from .__init__ import make_doc_template
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from reportlab.platypus import Paragraph, Spacer, KeepTogether, Table,\
    HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

from ..broadcast_timecode import TimecodeFormat
from ..docparser.adr_entity import ADRLine


def output_report(lines: List[ADRLine], tc_display_format: TimecodeFormat,
                  font_name="Helvetica"):
    character_numbers = set([n.character_id for n in lines])
    # pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    for n in character_numbers:
        char_lines = [line for line in lines
                      if not line.omitted and line.character_id == n]
        character_name = char_lines[0].character_name

        char_lines = sorted(char_lines, key=lambda line: line.start)

        title = "%s (%s) %s ADR Script" % (char_lines[0].title,
                                           character_name, n)
        filename = "%s_%s_%s_ADR Script.pdf" % (char_lines[0].title,
                                                n, character_name)

        doc = make_doc_template(page_size=letter, filename=filename,
                                document_title=title,
                                title=char_lines[0].title,
                                document_subheader=char_lines[0].spot or "",
                                supervisor=char_lines[0].supervisor or "",
                                client=char_lines[0].client or "",
                                document_header=character_name or "")

        story = []

        prompt_style = getSampleStyleSheet()['Normal']
        prompt_style.fontName = font_name
        prompt_style.fontSize = 18.

        prompt_style.leading = 24.
        prompt_style.leftIndent = 1.5 * inch
        prompt_style.rightIndent = 1.5 * inch

        number_style = getSampleStyleSheet()['Normal']
        number_style.fontName = font_name
        number_style.fontSize = 14

        number_style.leading = 24
        number_style.leftIndent = 0.
        number_style.rightIndent = 0.

        for line in char_lines:
            start_tc = tc_display_format.seconds_to_smpte(line.start)
            finish_tc = tc_display_format.seconds_to_smpte(line.finish)
            data_block = [[Paragraph(line.cue_number, number_style),
                           Paragraph(start_tc + " - " + finish_tc,
                                     number_style)
                           ]]

# RIGHTWARDS ARROW →
# Unicode: U+2192, UTF-8: E2 86 92
            story.append(
                KeepTogether(
                    [HRFlowable(width='50%', color=colors.black),
                     Table(data=data_block, colWidths=[1.5 * inch, 6. * inch],
                           style=[('LEFTPADDING', (0, 0), (-1, -1), 0.)]),
                     Paragraph(line.prompt, prompt_style),
                     Spacer(1., inch * 1.5)]
                )
            )

        doc.build(story)

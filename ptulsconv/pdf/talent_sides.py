# -*- coding: utf-8 -*-

from .common import make_doc_template
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from reportlab.platypus import Paragraph, Spacer, KeepTogether, Table, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def output_report(lines):
    character_numbers = set([n['Character Number'] for n in lines])
    pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    for n in character_numbers:
        char_lines = [line for line in lines
                 if 'Omit' not in line.keys() and line['Character Number'] == n]

        sorted(char_lines, key=lambda line: line['PT.Clip.Start_Seconds'])

        title = "%s (%s) %s ADR Script" % (char_lines[0]['Title'], char_lines[0]['Character Name'], n)
        filename = "%s_%s_%s_ADR Script.pdf" % (lines[0]['Title'], n, lines[0]['Character Name'])

        doc = make_doc_template(page_size=letter, filename=filename, document_title=title,
                                record=char_lines[0], document_header=char_lines[0]['Character Name'])

        story = []

        prompt_style = getSampleStyleSheet()['Normal']
        prompt_style.fontName = 'Futura'
        prompt_style.fontSize = 18

        prompt_style.leading = 24
        prompt_style.leftIndent = 1.5 * inch
        prompt_style.rightIndent = 1.5 * inch

        number_style = getSampleStyleSheet()['Normal']
        number_style.fontName = 'Futura'
        number_style.fontSize = 14

        number_style.leading = 24
        number_style.leftIndent = 0.
        number_style.rightIndent = 0.

        for line in char_lines:
            data_block = [[Paragraph(line['Cue Number'], number_style),
                           Paragraph(line['PT.Clip.Start'] + " - " + line['PT.Clip.Finish'], number_style)
                           ]]
# RIGHTWARDS ARROW →
# Unicode: U+2192, UTF-8: E2 86 92
            story.append(
                KeepTogether(
                    [HRFlowable(width='50%', color=colors.black),
                     Table(data=data_block, colWidths=[1.5 * inch, 6. * inch],
                           style=[('LEFTPADDING', (0, 0), (-1, -1), 0.)]),
                     Paragraph(line['Line'], prompt_style),
                     Spacer(1., inch * 1.5)]
                )
            )

        doc.build(story)

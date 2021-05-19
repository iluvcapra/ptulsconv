# -*- coding: utf-8 -*-

from .common import GRect, draw_title_block
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, \
    KeepTogether, Table, HRFlowable, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

page_box = GRect(inch * 0.5, inch * 0.5, letter[0] - inch, letter[1] - inch)
title_box, page_box = page_box.split_y(0.875 * inch, 'd')
header_block, title_block = title_box.split_x(inch * 4.)


def output_report(records):
    character_numbers = set([n['Character Number'] for n in records['events']])
    pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    for n in character_numbers:
        lines = [line for line in records['events']
                 if 'Omit' not in line.keys() and line['Character Number'] == n]

        page_template = PageTemplate(id="Main",
                                     frames=[Frame(page_box.min_x, page_box.min_y, page_box.width, page_box.height)],
                                     onPage=lambda canv, _: draw_title_block(canv, title_block, lines[0]))

        sorted(lines, key=lambda line: line['PT.Clip.Start_Seconds'])

        doc = BaseDocTemplate("%s_%s_Script.pdf" % (n, lines[0]['Character Name']),
                              pagesize=letter, leftMargin=0.5 * inch,
                              rightMargin=0.5 * inch, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

        doc.addPageTemplates([page_template])
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

        for line in lines:
            data_block = [[Paragraph(line['Cue Number'], number_style),
                           Paragraph(line['PT.Clip.Start'] + " - " + line['PT.Clip.Finish'], number_style)
                           ]]
# RIGHTWARDS ARRO→W
# Unicode: U+2192, UTF-8: E2 86 92
            story.append(
                KeepTogether(
                    [HRFlowable(width='100%', color=colors.black),
                     Table(data=data_block, colWidths=[1.5 * inch, 6. * inch]),
                     Paragraph(line['Line'], prompt_style),
                     Spacer(1., inch * 1.5)]
                )
            )

        doc.build(story)

from reportlab.pdfgen.canvas import Canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle

from .common import GRect

import datetime


def output_report(records):

    # CN
    # Role
    # Actor
    # R1, R2, R3, R4, R5, R6
    # Opt
    # TV
    # EFF
    # Total

    reel_numbers = sorted(set([x.get('Reel', None) for x in records['events'] if 'Reel' in x.keys()]))

    aux_columns = [{'heading': 'OPT', 'key': 'Optional'},
                   {'heading': 'TV', 'key': 'TV'},
                   {'heading': 'EFF', 'key': 'Effort'}]

    sorted_character_numbers = sorted(set([x['CN'] for x in records['events']]),
                                      key=lambda x: int(x))

    pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    page: GRect = GRect(0, 0, letter[1], letter[0])
    page = page.inset(inch * 0.5)

    headers = ['#', 'Role', 'Actor']

    if len(reel_numbers) > 0:
        for n in reel_numbers:
            headers.append(n)

    headers.append("Total")

    for m in aux_columns:
        headers.append(m['heading'])

    line_count_data = [headers]


    for cn in sorted_character_numbers:
        this_row = [cn]
        this_character_cues = [x for x in records['events'] if x['Character Number'] == cn]
        this_row.append(this_character_cues[0].get('Character Name', ""))
        this_row.append(this_character_cues[0].get('Actor Name', ""))

        if len(reel_numbers) > 0:
            for _ in reel_numbers:
                this_row.append("X")

        this_row.append(len([x for x in this_character_cues if 'Omit' not in x.keys()]))
        for m in aux_columns:
            this_row.append(0)

        line_count_data.append(this_row)
    pass

    style = TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Futura'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('LINEBELOW', (0, 0), (-1, 0), 1.0, colors.black),
                        ('ALIGN', (3, 1), (-1, -1), 'RIGHT')
                        ]
                       )

    table = Table(data=line_count_data, style=style, colWidths=[0.5 * inch, 1.25 * inch, 2. * inch, 0.5 * inch,
                                                                0.5 * inch, 0.5 * inch, 0.5 * inch, 0.5 * inch])

    c = Canvas('Line Count.pdf', pagesize=(letter[1], letter[0]))

    w, h = table.wrap(page.width, page.height)
    table.drawOn(canvas=c, x=page.min_x, y=page.max_y - h)

    c.showPage()
    c.save()

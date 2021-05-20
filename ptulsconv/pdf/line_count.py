from reportlab.pdfgen.canvas import Canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle

from .common import GRect, time_format, NumberedCanvas

import datetime


def build_columns(records, show_priorities = False):
    columns = list()
    reel_numbers = sorted(set([x.get('Reel', None) for x in records['events'] if 'Reel' in x.keys()]))

    def blank_len(iter):
        l = len(iter)
        if l == 0:
            return ""
        else:
            return str(l)

    columns.append({
        'heading': '#',
        'value_getter': lambda recs: recs[0]['Character Number'],
        'style_getter': lambda col_index: [],
        'width': 0.75 * inch
    })

    columns.append({
        'heading': 'Role',
        'value_getter': lambda recs: recs[0]['Character Name'],
        'style_getter': lambda col_index: [],
        'width': 1.75 * inch
    })

    columns.append({
        'heading': 'Actor',
        'value_getter': lambda recs: recs[0].get('Actor Name', ''),
        'style_getter': lambda col_index: [(('LINEAFTER'), (col_index, 0), (col_index, -1), 1.0, colors.black)],
        'width': 1.75 * inch
    })

    if len(reel_numbers) > 0:
        columns.append({
            'heading': 'RX',
            'value_getter': lambda recs: blank_len([r for r in recs if r.get('Reel', None) in ("", None)]),
            'style_getter': lambda col_index: [],
            'width': 0.5 * inch
        })

        for n in reel_numbers:
            columns.append({
                'heading': n,
                'value_getter': lambda recs: blank_len([r for r in recs if r['Reel'] == n]),
                'style_getter': lambda col_index: [],
                'width': 0.5 * inch
            })

    if show_priorities:
        for n in range(1, 6,):
            columns.append({
                'heading': 'P%i' % n,
                'value_getter': lambda recs: blank_len([r for r in recs if r.get('Priority', None) == n]),
                'style_getter': lambda col_index: [],
                'width': 0.375 * inch
            })

        columns.append({
            'heading': '>P5',
            'value_getter': lambda recs: blank_len([r for r in recs if r.get('Priority', 5) > 5]),
            'style_getter': lambda col_index: [],
            'width': 0.5 * inch
        })

    columns.append({
        'heading': 'TV',
        'value_getter': lambda recs: blank_len([r for r in recs if 'TV' in r.keys()]),
        'style_getter': lambda col_index: [],
        'width': 0.5 * inch
    })

    columns.append({
        'heading': 'OPT',
        'value_getter': lambda recs: blank_len([r for r in recs if 'Optional' in r.keys()]),
        'style_getter': lambda col_index: [],
        'width': 0.5 * inch
    })

    columns.append({
        'heading': 'EFF',
        'value_getter': lambda recs: blank_len([r for r in recs if 'Effort' in r.keys()]),
        'style_getter': lambda col_index: [],
        'width': 0.5 * inch
    })

    columns.append({
        'heading': 'Total',
        'value_getter': lambda recs: len([r for r in recs]),
        'style_getter': lambda col_index: [(('LINEBEFORE'), (col_index, 0), (col_index, -1), 1.0, colors.black),
                                           ('ALIGN', (col_index, 0), (col_index, -1), 'RIGHT')],
        'width': inch
    })

    columns.append({
        'heading': 'Studio Time',
        'value_getter': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.) for r in recs])),
        'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'RIGHT')],
        'width': inch
    })

    return columns


def populate_columns(records, columns):
    data = list()
    styles = list()
    columns_widths = list()

    sorted_character_numbers = sorted(set([x['CN'] for x in records['events']]),
                                      key=lambda x: int(x))

    # construct column styles

    for i, c in enumerate(columns):
        styles.extend(c['style_getter'](i))
        columns_widths.append(c['width'])

    # construct data table
    # headers
    data.append(list(map(lambda x: x['heading'], columns)))

    # values
    for n in sorted_character_numbers:
        char_records = sorted([x for x in records['events'] if x['Character Number'] == n],
                              key=lambda x: x['PT.Clip.Start_Seconds'])
        row_data = list()
        for col in columns:
            row_data.append(col['value_getter'](char_records))

        data.append(row_data)

    return data, styles, columns_widths


def output_report(records):
    # CN
    # Role
    # Actor
    # R1, R2, R3, R4, R5, R6
    # Opt
    # TV
    # EFF
    # Total

    columns = build_columns(records)
    data, style, columns_widths = populate_columns(records, columns)
    style.append(('FONTNAME', [0, 0], (-1, -1), "Futura"))
    style.append(('FONTSIZE', (0, 0), (-1, -1), 11))
    style.append(('LINEBELOW', (0, 0), (-1, 0), 1.0, colors.black))
    style.append(('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray))

    pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    page: GRect = GRect(0, 0, letter[1], letter[0])
    page = page.inset(inch * 0.5)
    title_box, table_box = page.split_y(inch, 'd')

    c = NumberedCanvas('%s Line Count.pdf' % records['events'][0]['Title'], pagesize=(letter[1], letter[0]))
    c.setFont('Futura', 18.)
    c.drawCentredString(title_box.center_x, title_box.center_y, "Line Count")

    table = Table(data=data, style=style, colWidths=columns_widths)

    w, h = table.wrap(table_box.width, table_box.height)
    table.drawOn(canvas=c,
                 x=table_box.min_x + table_box.width / 2. - w / 2.,
                 y=table_box.max_y - h)

    c.showPage()
    c.save()

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib import colors

from reportlab.platypus import Table

from .common import time_format, make_doc_template


def build_columns(records, show_priorities=False, include_omitted=False):
    columns = list()
    reel_numbers = sorted(set([x['Reel'] for x in records['events'] if 'Reel' in x.keys()]))

    num_column_width = 0.375 * inch

    columns.append({
        'heading': '#',
        'value_getter': lambda recs: recs[0]['Character Number'],
        'value_getter2': lambda recs: "",
        'style_getter': lambda col_index: [],
        'width': 0.375 * inch,
        'summarize': False
    })

    columns.append({
        'heading': 'Role',
        'value_getter': lambda recs: recs[0]['Character Name'],
        'value_getter2': lambda recs: recs[0].get('Actor Name', ""),
        'style_getter': lambda col_index: [('LINEAFTER', (col_index, 0), (col_index, -1), 1.0, colors.black)],
        'width': 1.75 * inch,
        'summarize': False
    })

    if len(reel_numbers) > 0:
        # columns.append({
        #     'heading': 'RX',
        #     'value_getter': lambda recs: blank_len([r for r in recs if 'Reel' not in r.keys()]),
        #     'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.) for r in recs
        #                                                    if 'Reel' not in r.keys()])),
        #     'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'CENTER')],
        #     'width': num_column_width
        # })

        for n in reel_numbers:
            columns.append({
                'heading': n,
                'value_getter': lambda recs, n1=n: len([r for r in recs if r['Reel'] == n1]),
                'value_getter2': lambda recs, n1=n: time_format(sum([r.get('Time Budget Mins', 0.) for r in recs
                                                               if r['Reel'] == n1])),
                'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'CENTER'),
                                                   ('LINEAFTER', (col_index, 0), (col_index, -1), .5, colors.gray)],
                'width': num_column_width
            })

    if show_priorities:
        for n in range(1, 6,):
            columns.append({
                'heading': 'P%i' % n,
                'value_getter': lambda recs: len([r for r in recs if r.get('Priority', None) == n]),
                'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.)
                                                               for r in recs if r.get('Priority', None) == n])),
                'style_getter': lambda col_index: [],
                'width': num_column_width
            })

        columns.append({
            'heading': '>P5',
            'value_getter': lambda recs: len([r for r in recs if r.get('Priority', 5) > 5]),
            'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.)
                                                           for r in recs if r.get('Priority', 5) > 5])),
            'style_getter': lambda col_index: [],
            'width': num_column_width
        })

    columns.append({
        'heading': 'TV',
        'value_getter': lambda recs: len([r for r in recs if 'TV' in r.keys()]),
        'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.)
                                                       for r in recs if 'TV' in r.keys()])),
        'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'CENTER'),
                                           ('LINEBEFORE', (col_index, 0), (col_index, -1), 1., colors.black),
                                           ('LINEAFTER', (col_index, 0), (col_index, -1), .5, colors.gray)],
        'width': num_column_width
    })

    columns.append({
        'heading': 'Opt',
        'value_getter': lambda recs: len([r for r in recs if 'Optional' in r.keys()]),
        'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.)
                                                       for r in recs if 'Optional' in r.keys()])),
        'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'CENTER'),
                                           ('LINEAFTER', (col_index, 0), (col_index, -1), .5, colors.gray)],
        'width': num_column_width
    })

    columns.append({
        'heading': 'Eff',
        'value_getter': lambda recs: len([r for r in recs if 'Effort' in r.keys()]),
        'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins',0.)
                                                  for r in recs if 'Effort' in r.keys()])),
        'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'CENTER')],
        'width': num_column_width
    })

    if include_omitted:
        columns.append({
            'heading': 'Omit',
            'value_getter': lambda recs: len([r for r in recs if 'Omitted' in r.keys()]),
            'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.)
                                                           for r in recs if 'Omitted' in r.keys()])),
            'style_getter': lambda col_index: [('ALIGN', (col_index, 0), (col_index, -1), 'CENTER')],
            'width': num_column_width
        })

    columns.append({
        'heading': 'Total',
        'value_getter': lambda recs: len([r for r in recs if 'Omitted' not in r.keys()]),
        'value_getter2': lambda recs: time_format(sum([r.get('Time Budget Mins', 0.)
                                                       for r in recs if 'Omitted' not in r.keys()]), zero_str=None),
        'style_getter': lambda col_index: [('LINEBEFORE', (col_index, 0), (col_index, -1), 1.0, colors.black),
                                           ('ALIGN', (col_index, 0), (col_index, -1), 'CENTER')],
        'width': 0.5 * inch
    })

    return columns


def populate_columns(records, columns, include_omitted, page_size):
    data = list()
    styles = list()
    columns_widths = list()

    sorted_character_numbers = sorted(set([x['Character Number'] for x in records['events']
                                          if 'Character Number' in x.keys()]),
                                      key=lambda x: str(x))

    # construct column styles

    for i, c in enumerate(columns):
        styles.extend(c['style_getter'](i))
        columns_widths.append(c['width'])

    data.append(list(map(lambda x: x['heading'], columns)))

    if include_omitted:
        lines = [x for x in records['events']]
    else:
        lines = [x for x in records['events'] if 'Omitted' not in x.keys()]

    for n in sorted_character_numbers:
        char_records = list([x for x in lines if x['Character Number'] == n])
        row_data = list()
        row_data2 = list()
        for col in columns:
            row1_index = len(data)
            row2_index = row1_index + 1
            row_data.append(col['value_getter'](list(char_records)))
            row_data2.append(col['value_getter2'](list(char_records)))
            styles.extend([('TEXTCOLOR', (0, row2_index), (-1, row2_index), colors.red),
                           ('LINEBELOW', (0, row2_index), (-1, row2_index), 0.5, colors.black)])

        data.append(row_data)
        data.append(row_data2)

    summary_row1 = list()
    summary_row2 = list()
    row1_index = len(data)

    for col in columns:
        if col.get('summarize', True):
            summary_row1.append(col['value_getter'](lines))
            summary_row2.append(col['value_getter2'](lines))
        else:
            summary_row1.append("")
            summary_row2.append("")

    styles.append(('LINEABOVE', (0, row1_index), (-1, row1_index), 2.0, colors.black))

    data.append(summary_row1)
    data.append(summary_row2)

    return data, styles, columns_widths


def output_report(records, include_omitted=False, page_size=portrait(letter)):
    columns = build_columns(records, include_omitted)
    data, style, columns_widths = populate_columns(records, columns, include_omitted, page_size)
    style.append(('FONTNAME', (0, 0), (-1, -1), "Futura"))
    style.append(('FONTSIZE', (0, 0), (-1, -1), 9.))
    style.append(('LINEBELOW', (0, 0), (-1, 0), 1.0, colors.black))
    style.append(('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray))

    pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    title = "%s Line Count" % (records['events'][0]['Title'])
    filename = title + '.pdf'
    doc = make_doc_template(page_size=page_size, filename=filename,
                            document_title=title,
                            record=records['events'][0],
                            document_header='Line Count')

    table = Table(data=data, style=style, colWidths=columns_widths)

    doc.build([table])

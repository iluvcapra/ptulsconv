from typing import List, Optional

# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib import colors

from reportlab.platypus import Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .__init__ import time_format, make_doc_template
from ..docparser.adr_entity import ADRLine


def build_columns(lines: List[ADRLine], reel_list: Optional[List[str]],
                  show_priorities=False, include_omitted=False):
    columns = list()
    reel_numbers = reel_list or sorted(
        set([x.reel for x in lines if x.reel is not None])
    )

    num_column_width = 15. / 32. * inch

    columns.append({
        'heading': '#',
        'value_getter': lambda recs: recs[0].character_id,
        'value_getter2': lambda recs: "",
        'style_getter': lambda col_index: [],
        'width': 0.375 * inch,
        'summarize': False
    })

    columns.append({
        'heading': 'Role',
        'value_getter': lambda recs: recs[0].character_name,
        'value_getter2': lambda recs: recs[0].actor_name or "",
        'style_getter': lambda col_index: [('LINEAFTER',
                                            (col_index, 0),
                                            (col_index, -1),
                                            1.0, colors.black)],
        'width': 1.75 * inch,
        'summarize': False
    })

    columns.append({
        'heading': 'TV',
        'value_getter': lambda recs: len([r for r in recs if r.tv]),
        'value_getter2': (lambda recs:
                          time_format(sum([r.time_budget_mins or 0.
                                           for r in recs if r.tv]))
                          ),
        'style_getter': (lambda col_index:
                         [('ALIGN', (col_index, 0), (col_index, -1),
                           'CENTER'),
                          ('LINEBEFORE', (col_index, 0), (col_index, -1),
                           1., colors.black),
                          ('LINEAFTER', (col_index, 0), (col_index, -1),
                           .5, colors.gray)]
                         ),
        'width': num_column_width
    })

    columns.append({
        'heading': 'Opt',
        'value_getter': lambda recs: len([r for r in recs if r.optional]),
        'value_getter2': (lambda recs:
                          time_format(sum([r.time_budget_mins or 0.
                                           for r in recs if r.optional]))
                          ),
        'style_getter': (lambda col_index:
                         [('ALIGN', (col_index, 0), (col_index, -1),
                           'CENTER'),
                          ('LINEAFTER', (col_index, 0), (col_index, -1),
                           .5, colors.gray)]
                         ),
        'width': num_column_width
    })

    columns.append({
        'heading': 'Eff',
        'value_getter': lambda recs: len([r for r in recs if r.effort]),
        'value_getter2': (lambda recs:
                          time_format(sum([r.time_budget_mins or 0.
                                           for r in recs if r.effort]))
                          ),
        'style_getter': (lambda col_index:
                         [('ALIGN', (col_index, 0), (col_index, -1),
                           'CENTER')]
                         ),
        'width': num_column_width
    })

    columns.append({
        'heading': '',
        'value_getter': lambda _: '',
        'value_getter2': lambda _: '',
        'style_getter': lambda col_index: [
            ('LINEBEFORE', (col_index, 0), (col_index, -1), 1., colors.black),
            ('LINEAFTER', (col_index, 0), (col_index, -1), 1., colors.black),
        ],
        'width': 2.
    })

    if len(reel_numbers) > 0:

        for n in reel_numbers:
            columns.append({
                'heading': n,
                'value_getter': (lambda recs, n1=n:
                                 len([r for r in recs if r.reel == n1])
                                 ),
                'value_getter2': (lambda recs, n1=n:
                                  time_format(sum([r.time_budget_mins or 0.
                                                   for r in recs
                                                   if r.reel == n1]))
                                  ),
                'style_getter': (lambda col_index:
                                 [('ALIGN', (col_index, 0), (col_index, -1),
                                   'CENTER'),
                                  ('LINEAFTER', (col_index, 0),
                                   (col_index, -1),
                                   .5, colors.gray)]
                                 ),

                'width': num_column_width
            })

    if show_priorities:
        for n in range(1, 6,):
            columns.append({
                'heading': 'P%i' % n,
                'value_getter': lambda recs: len([r for r in recs
                                                  if r.priority == n]),
                'value_getter2': (lambda recs:
                                  time_format(sum([r.time_budget_mins or 0.
                                                   for r in recs
                                                   if r.priority == n]))
                                  ),
                'style_getter': lambda col_index: [],
                'width': num_column_width
            })

        columns.append({
            'heading': '>P5',
            'value_getter': lambda recs: len([r for r in recs
                                              if (r.priority or 5) > 5]),
            'value_getter2': (lambda recs:
                              time_format(sum([r.time_budget_mins or 0.
                                               for r in recs
                                               if (r.priority or 5) > 5]))
                              ),
            'style_getter': lambda col_index: [],
            'width': num_column_width
        })

    if include_omitted:
        columns.append({
            'heading': 'Omit',
            'value_getter': lambda recs: len([r for r in recs if r.omitted]),
            'value_getter2': (lambda recs:
                              time_format(sum([r.time_budget_mins or 0.
                                               for r in recs if r.omitted]))),
            'style_getter': (lambda col_index:
                             [('ALIGN', (col_index, 0), (col_index, -1),
                               'CENTER')]
                             ),
            'width': num_column_width
        })

    columns.append({
        'heading': 'Total',
        'value_getter': lambda recs: len([r for r in recs if not r.omitted]),
        'value_getter2': (lambda recs:
                          time_format(
                              sum([r.time_budget_mins or 0.

                                   for r in recs if not r.omitted])
                          )
                          ),
        'style_getter': (lambda col_index:
                         [('LINEBEFORE', (col_index, 0), (col_index, -1),
                           1.0, colors.black),
                          ('ALIGN', (col_index, 0), (col_index, -1),
                           'CENTER')]
                         ),
        'width': 0.5 * inch
    })

    return columns


def populate_columns(lines: List[ADRLine], columns, include_omitted,
                     _page_size):
    data = list()
    styles = list()
    columns_widths = list()

    sorted_character_numbers: List[str] = sorted(
        set([x.character_id for x in lines]),
        key=lambda x: str(x))

    # construct column styles

    for i, c in enumerate(columns):
        styles.extend(c['style_getter'](i))
        columns_widths.append(c['width'])

    data.append(list(map(lambda x: x['heading'], columns)))

    if not include_omitted:
        lines = [x for x in lines if not x.omitted]

    for n in sorted_character_numbers:
        char_records = [x for x in lines if x.character_id == n]
        if len(char_records) > 0:
            row_data = list()
            row_data2 = list()

            for col in columns:
                row1_index = len(data)
                row2_index = row1_index + 1
                row_data.append(col['value_getter'](list(char_records)))
                row_data2.append(col['value_getter2'](list(char_records)))

                styles.extend([('TEXTCOLOR', (0, row2_index), (-1, row2_index),
                                colors.red),
                               ('LINEBELOW', (0, row2_index), (-1, row2_index),
                                0.5, colors.black)])

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

    styles.append(('LINEABOVE', (0, row1_index), (-1, row1_index), 2.0,
                   colors.black))

    data.append(summary_row1)
    data.append(summary_row2)

    return data, styles, columns_widths


# def build_header(column_widths):
#     pass


def output_report(lines: List[ADRLine], reel_list: List[str],
                  include_omitted=False, page_size=portrait(letter),
                  font_name='Helvetica'):
    columns = build_columns(lines, include_omitted=include_omitted,
                            reel_list=reel_list)
    data, style, columns_widths = populate_columns(lines, columns,
                                                   include_omitted, page_size)

    style.append(('FONTNAME', (0, 0), (-1, -1), font_name))
    style.append(('FONTSIZE', (0, 0), (-1, -1), 9.))
    style.append(('LINEBELOW', (0, 0), (-1, 0), 1.0, colors.black))
    # style.append(('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray))

    # pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    title = "%s Line Count" % lines[0].title
    filename = title + '.pdf'
    doc = make_doc_template(page_size=page_size, filename=filename,
                            document_title=title, title=lines[0].title,
                            document_subheader=lines[0].spot,
                            client=lines[0].client,
                            supervisor=lines[0].supervisor,
                            document_header='Line Count')

    # header_data, header_style, header_widths = build_header(columns_widths)
    # header_table = Table(data=header_data, style=header_style,
    # colWidths=header_widths)

    table = Table(data=data, style=style, colWidths=columns_widths)

    story = [Spacer(height=0.5 * inch, width=1.), table]

    style = getSampleStyleSheet()['Normal']
    style.fontName = font_name
    style.fontSize = 12.
    style.spaceBefore = 16.
    style.spaceAfter = 16.

    omitted_count = len([x for x in lines if x.omitted])

    if not include_omitted and omitted_count > 0:
        story.append(Paragraph("* %i Omitted lines are excluded." %
                     omitted_count, style))

    doc.build(story)

# -*- coding: utf-8 -*-

from .common import time_format, make_doc_template
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, portrait

from reportlab.platypus import Paragraph, Spacer, KeepTogether, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def build_aux_data_field(line):
    entries = list()
    if 'Reason' in line.keys():
        entries.append("Reason: " + line["Reason"])
    if 'Note' in line.keys():
        entries.append("Note: " + line["Note"])
    if 'Requested by' in line.keys():
        entries.append("Requested by: " + line["Requested by"])
    if 'Shot' in line.keys():
        entries.append("Shot: " + line["Shot"])

    tag_field = ""
    for tag in line.keys():
        if line[tag] == tag and tag != 'ADR':
            tag_field += "<font backColor=black textColor=white>" + tag + "</font> "

    entries.append(tag_field)

    return "<br />".join(entries)


def build_story(lines):
    story = list()

    this_scene = None
    scene_style = getSampleStyleSheet()['Normal']
    scene_style.fontName = 'Futura'
    scene_style.leftIndent = 0.
    scene_style.leftPadding = 0.
    scene_style.spaceAfter = 18.
    line_style = getSampleStyleSheet()['Normal']
    line_style.fontName = 'Futura'

    for line in lines:
        table_style = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
                       ('LEFTPADDING', (0, 0), (0, 0), 0.0),
                       ('BOTTOMPADDING', (0, 0), (-1, -1), 24.)]

        if 'Omitted' in line.keys():
            cue_number_field = "<s>" + line['Cue Number'] + "</s><br /><font fontSize=7>" + \
                               line['Character Name'] + "</font>"
            table_style.append(('BACKGROUND', (0, 0), (-1, 0), colors.lightpink))
        elif 'Effort' in line.keys():
            cue_number_field = "<s>" + line['Cue Number'] + "</s><br /><font fontSize=7>" + \
                               line['Character Name'] + "</font>"
            table_style.append(('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen))
        else:
            cue_number_field = line['Cue Number'] + "<br /><font fontSize=7>" + line['Character Name'] + "</font>"

        time_data = time_format(line.get('Time Budget Mins', 0.))

        if 'Priority' in line.keys():
            time_data = time_data + "<br />" + "P: " + int(line['Priority'])

        aux_data_field = build_aux_data_field(line)

        line_table_data = [[Paragraph(cue_number_field, line_style),
                            Paragraph(line['PT.Clip.Start'] + "<br />" + line['PT.Clip.Finish'], line_style),
                            Paragraph(line['Line'], line_style),
                            Paragraph(time_data, line_style),
                            Paragraph(aux_data_field, line_style)
                            ]]

        line_table = Table(data=line_table_data,
                           colWidths=[inch * 1., inch, inch * 3., 0.5 * inch, inch * 2.],
                           style=table_style)

        if line.get('Scene', "[No Scene]") != this_scene:
            this_scene = line.get('Scene', "[No Scene]")
            story.append(KeepTogether([
                Spacer(1., 0.25 * inch),
                Paragraph("<u>" + this_scene + "</u>", scene_style),
                line_table]))
        else:
            line_table.setStyle(table_style)
            story.append(KeepTogether([line_table]))

    return story


def output_report(records, page_size=portrait(letter)):
    lines = sorted(records['events'], key=lambda line: line['PT.Clip.Start_Seconds'])

    title = "%s ADR Report" % (lines[0]['Title'])
    filename = title + ".pdf"

    doc = make_doc_template(page_size=page_size,
                            filename=filename, document_title=title,
                            record=lines[0], document_header='ADR Report')

    story = build_story(lines)

    doc.build(story)

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
            fcolor = 'white'
            bcolor = 'black'
            if tag == 'ADLIB' or tag == 'TBW':
                bcolor = 'darkmagenta'
            elif tag == 'EFF':
                bcolor = 'red'
            elif tag == 'TV':
                bcolor = 'blue'

            tag_field += "<font backColor=%s textColor=%s fontSize=11>%s</font> " % (bcolor, fcolor, tag)

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

        cue_number_field = "%s<br /><font fontSize=7>%s</font>" % (line['Cue Number'], line['Character Name'])

        time_data = time_format(line.get('Time Budget Mins', 0.))

        if 'Priority' in line.keys():
            time_data = time_data + "<br />" + "P: " + int(line['Priority'])

        aux_data_field = build_aux_data_field(line)

        tc_data = build_tc_data(line)

        line_table_data = [[Paragraph(cue_number_field, line_style),
                            Paragraph(tc_data, line_style),
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


def build_tc_data(line):
    tc_data = line['PT.Clip.Start'] + "<br />" + line['PT.Clip.Finish']
    third_line = []
    if 'Reel' in line.keys():
        if line['Reel'][0:1] == 'R':
            third_line.append("%s" % (line['Reel']))
        else:
            third_line.append("Reel %s" % (line['Reel']))
    if 'Version' in line.keys():
        third_line.append("(%s)" % line['Version'])
    if len(third_line) > 0:
        tc_data = tc_data + "<br/>" + " ".join(third_line)
    return tc_data


def generate_report(page_size, lines, character_number=None, include_done=True,
                    include_omitted=True):
    if character_number is not None:
        lines = [r for r in lines if r['Character Number'] == character_number]
        title = "%s ADR Report (%s)" % (lines[0]['Title'], lines[0]['Character Name'])
        document_header = "%s ADR Report" % (lines[0]['Character Name'])
    else:
        title = "%s ADR Report" % (lines[0]['Title'])
        document_header = 'ADR Report'

    if not include_done:
        lines = [line for line in lines if 'Done' not in line.keys()]

    if not include_omitted:
        lines = [line for line in lines if 'Omitted' not in line.keys()]

    lines = sorted(lines, key=lambda line: line['PT.Clip.Start_Seconds'])

    filename = title + ".pdf"
    doc = make_doc_template(page_size=page_size,
                            filename=filename, document_title=title,
                            record=lines[0], document_header=document_header)
    story = build_story(lines)
    doc.build(story)


def output_report(lines, page_size=portrait(letter), by_character=False):
    if by_character:
        character_numbers = set((r['Character Number'] for r in lines))
        for n in character_numbers:
            generate_report(page_size, lines, n)
    else:
        generate_report(page_size, lines)

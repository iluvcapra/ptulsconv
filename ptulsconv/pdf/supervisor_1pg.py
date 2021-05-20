from reportlab.pdfgen.canvas import Canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

from .common import GRect, draw_title_block

import datetime


def draw_header_block(canvas, rect, record):
    rect.draw_text_cell(canvas, record['Cue Number'], "Helvetica", 44, vertical_align='m')

def draw_character_row(canvas, rect, record):
    label_frame, value_frame = rect.split_x(1.25 * inch)
    label_frame.draw_text_cell(canvas, "CHARACTER", "Futura", 10, force_baseline=9.)
    line = "%s / %s " % (record['Character Number'], record['Character Name'])
    if 'Actor Name' in record.keys():
        line = line + " / " + record['Actor Name']
    value_frame.draw_text_cell(canvas, line, "Futura", 12, force_baseline=9.)
    rect.draw_border(canvas, ['min_y', 'max_y'])


def draw_cue_number_block(canvas, rect, record):
    (label_frame, number_frame,), aux_frame = rect.divide_y([0.20 * inch, 0.375 * inch], direction='d')
    label_frame.draw_text_cell(canvas, "CUE NUMBER", "Futura", 10,
                               inset_y=5., vertical_align='t')
    number_frame.draw_text_cell(canvas, record['Cue Number'], "Futura", 14,
                                inset_x=10., inset_y=2., draw_baseline=True)

    tags = ['TV', 'OPT', 'ADLIB', 'EFF', 'TBW', 'OMIT']
    tag_field = ""
    for tag in tags:
        if tag in record.keys():
            tag_field = tag_field + tag + " "

    aux_frame.draw_text_cell(canvas, tag_field, "Futura", 10,
                             inset_x=10., inset_y=2., vertical_align='t')
    rect.draw_border(canvas, 'max_x')


def draw_timecode_block(canvas, rect, record):
    (in_label_frame, in_frame, out_label_frame, out_frame), _ = rect.divide_y(
        [0.20 * inch, 0.25 * inch, 0.20 * inch, 0.25 * inch], direction='d')

    in_label_frame.draw_text_cell(canvas, "IN", "Futura", 10,
                                  vertical_align='t', inset_y=5., inset_x=5.)
    in_frame.draw_text_cell(canvas, record['PT.Clip.Start'], "Futura", 14,
                            inset_x=10., inset_y=2., draw_baseline=True)
    out_label_frame.draw_text_cell(canvas, "OUT", "Futura", 10,
                                   vertical_align='t', inset_y=5., inset_x=5.)
    out_frame.draw_text_cell(canvas, record['PT.Clip.Finish'], "Futura", 14,
                             inset_x=10., inset_y=2., draw_baseline=True)

    rect.draw_border(canvas, 'max_x')


def draw_reason_block(canvas, rect, record):
    reason_cell, notes_cell = rect.split_y(24., direction='d')
    reason_label, reason_value = reason_cell.split_x(.75 * inch)
    notes_label, notes_value = notes_cell.split_x(.75 * inch)

    reason_label.draw_text_cell(canvas, "Reason:", "Futura", 12,
                                inset_x=5., inset_y=5., vertical_align='b')
    reason_value.draw_text_cell(canvas, record.get("Reason", ""), "Futura", 12,
                                inset_x=5., inset_y=5., draw_baseline=True,
                                vertical_align='b')
    notes_label.draw_text_cell(canvas, "Note:", "Futura", 12,
                               inset_x=5., inset_y=5., vertical_align='t')

    style = getSampleStyleSheet()['BodyText']
    style.fontName = 'Futura'
    style.fontSize = 12
    style.leading = 14

    p = Paragraph(record.get("Note", ""), style)

    notes_value.draw_flowable(canvas, p, draw_baselines=True, inset_x=5., inset_y=5.)


def draw_prompt(canvas, rect, prompt=""):
    label, block = rect.split_y(0.20 * inch, direction='d')

    label.draw_text_cell(canvas, "PROMPT", "Futura", 10, vertical_align='t', inset_y=5., inset_x=0.)

    style = getSampleStyleSheet()['BodyText']
    style.fontName = 'Futura'
    style.fontSize = 14

    style.leading = 24
    style.leftIndent = 1.5 * inch
    style.rightIndent = 1.5 * inch

    p = Paragraph(prompt, style)

    block.draw_flowable(canvas, p, draw_baselines=True)

    rect.draw_border(canvas, 'max_y')


def draw_notes(canvas, rect, note=""):
    label, block = rect.split_y(0.20 * inch, direction='d')

    label.draw_text_cell(canvas, "NOTES", "Futura", 10, vertical_align='t', inset_y=5., inset_x=0.)

    style = getSampleStyleSheet()['BodyText']
    style.fontName = 'Futura'
    style.fontSize = 14
    style.leading = 24

    prompt = Paragraph(note, style)

    block.draw_flowable(canvas, prompt, draw_baselines=True)

    rect.draw_border(canvas, ['max_y', 'min_y'])


def draw_take_grid(canvas, rect):
    canvas.saveState()

    cp = canvas.beginPath()
    cp.rect(rect.min_x, rect.min_y, rect.width, rect.height)
    canvas.clipPath(cp, stroke=0, fill=0)

    canvas.setDash([3.0, 2.0])

    for xi in range(1, 10):
        x = xi * (rect.width / 10)
        if xi % 5 == 0:
            canvas.setDash(1, 0)
        else:
            canvas.setDash([2, 5])

        ln = canvas.beginPath()
        ln.moveTo(rect.min_x + x, rect.min_y)
        ln.lineTo(rect.min_x + x, rect.max_y)
        canvas.drawPath(ln)

    for yi in range(1, 10):
        y = yi * (rect.height / 6)
        if yi % 2 == 0:
            canvas.setDash(1, 0)
        else:
            canvas.setDash([2, 5])

        ln = canvas.beginPath()
        ln.moveTo(rect.min_x, rect.min_y + y)
        ln.lineTo(rect.max_x, rect.min_y + y)
        canvas.drawPath(ln)

    rect.draw_border(canvas, 'max_x')

    canvas.restoreState()


def draw_aux_block(canvas, rect, recording_time_sec_this_line, recording_time_sec):
    rect.draw_border(canvas, 'min_x')

    content_rect = rect.inset_xy(10., 10.)
    lines, last_line = content_rect.divide_y([12., 12., 24., 24., 24., 24.], direction='d')

    lines[0].draw_text_cell(canvas,
                            "Time for this line: %.1f mins" % (recording_time_sec_this_line / 60.), "Futura", 9.)
    lines[1].draw_text_cell(canvas, "Running time: %03.1f mins" % (recording_time_sec / 60.), "Futura", 9.)
    lines[2].draw_text_cell(canvas, "Actual Start: ______________", "Futura", 9., vertical_align='b')
    lines[3].draw_text_cell(canvas, "Record Date: ______________", "Futura", 9., vertical_align='b')
    lines[4].draw_text_cell(canvas, "Engineer: ______________", "Futura", 9., vertical_align='b')
    lines[5].draw_text_cell(canvas, "Location: ______________", "Futura", 9., vertical_align='b')


def draw_footer(canvas, rect, record, report_date, line_no, total_lines):
    rect.draw_border(canvas, 'max_y')
    report_date_s = [report_date.strftime("%c")]
    spotting_name = record.get('Spotting', [])
    pages_s = ["Line %i of %i" % (line_no, total_lines)]
    footer_s = " - ".join(report_date_s + spotting_name + pages_s)
    rect.draw_text_cell(canvas, footer_s, font_name="Futura", font_size=10., inset_y=2.)


def create_report_for_character(records, report_date):

    outfile = "%s_%s_%s_Log.pdf" % (records[0]['Title'], records[0]['Character Number'], records[0]['Character Name'],)
    assert outfile is not None
    assert outfile[-4:] == '.pdf', "Output file must have 'pdf' extension!"

    pdfmetrics.registerFont(TTFont('Futura', 'Futura.ttc'))

    page: GRect = GRect(0, 0, letter[0], letter[1])
    page = page.inset(inch * 0.5)
    (header_row, char_row, data_row, prompt_row, notes_row, takes_row), footer = \
        page.divide_y([0.875 * inch, 0.375 * inch, inch, 3.0 * inch, 1.5 * inch, 3 * inch], direction='d')

    cue_header_block, title_header_block = header_row.split_x(4.0 * inch)
    (cue_number_block, timecode_block), reason_block = data_row.divide_x([1.5 * inch, 1.5 * inch])
    (take_grid_block), aux_block = takes_row.split_x(5.25 * inch)

    c = Canvas(outfile, pagesize=letter)

    recording_time_sec = 0.0
    total_lines = len(records)
    line_n = 1
    for record in records:
        recording_time_sec_this_line: float = record.get('Time Budget Mins', 6.0) * 60.0
        recording_time_sec = recording_time_sec + recording_time_sec_this_line

        draw_header_block(c, cue_header_block, record)
        draw_title_block(c, title_header_block, record)
        draw_character_row(c, char_row, record)
        draw_cue_number_block(c, cue_number_block, record)
        draw_timecode_block(c, timecode_block, record)
        draw_reason_block(c, reason_block, record)
        draw_prompt(c, prompt_row, prompt=record['Line'])
        draw_notes(c, notes_row, note="")
        draw_take_grid(c, take_grid_block)
        draw_aux_block(c, aux_block, recording_time_sec_this_line, recording_time_sec)

        draw_footer(c, footer, record, report_date, line_no=line_n, total_lines=total_lines)
        line_n = line_n + 1

        c.showPage()

    c.save()


def output_report(records):
    report_date = datetime.datetime.now()
    events = sorted(records['events'], key=lambda x: x['PT.Clip.Start_Frames'])
    character_numbers = set([x['CN'] for x in events])

    for n in character_numbers:
        create_report_for_character([e for e in events if e['CN'] == n], report_date)

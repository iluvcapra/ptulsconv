from __future__ import annotations

from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, Spacer, Table

from ptulsconv.broadcast_timecode import TimecodeFormat
from ptulsconv.docparser.adr_entity import ADRLine

from .__init__ import make_doc_template, time_format


def build_aux_data_field(line: ADRLine):
    entries = []
    if line.reason is not None:
        entries.append("Reason: " + line.reason)
    if line.note is not None:
        entries.append("Note: " + line.note)
    if line.requested_by is not None:
        entries.append("Requested by: " + line.requested_by)
    if line.shot is not None:
        entries.append("Shot: " + line.shot)

    fg_color = "white"
    tag_field = ""
    if line.effort:
        bg_color = "red"
        tag_field += (
            f"<font backColor={bg_color} textColor={fg_color} fontSize=11>EFF</font> "
        )
    elif line.tv:
        bg_color = "blue"
        tag_field += (
            f"<font backColor={bg_color} textColor={fg_color} fontSize=11>TV</font> "
        )
    elif line.adlib:
        bg_color = "purple"
        tag_field += (
            f"<font backColor={bg_color} textColor={fg_color} fontSize=11>ADLIB</font> "
        )
    elif line.optional:
        bg_color = "green"
        tag_field += f"font backColor={bg_color} textColor={fg_color} fontSize=11>OPTIONAL</font>"

    entries.append(tag_field)

    return "<br />".join(entries)


def build_story(lines: list[ADRLine], tc_rate: TimecodeFormat, font_name="Helvetica"):
    story = []

    this_scene = None
    scene_style = getSampleStyleSheet()["Normal"]
    scene_style.fontName = font_name
    scene_style.leftIndent = 0.0
    scene_style.leftPadding = 0.0
    scene_style.spaceAfter = 18.0
    line_style = getSampleStyleSheet()["Normal"]
    line_style.fontName = font_name

    for line in lines:
        table_style = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, 0), 0.0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 24.0),
        ]

        cue_number_field = (
            f"{line.cue_number}<br /><font fontSize=7>{line.character_name}</font>"
        )

        time_data = time_format(line.time_budget_mins)

        if line.priority is not None:
            time_data = time_data + "<br />" + "P: " + str(line.priority)

        aux_data_field = build_aux_data_field(line)

        tc_data = build_tc_data(line, tc_rate)

        line_table_data = [
            [
                Paragraph(cue_number_field, line_style),
                Paragraph(tc_data, line_style),
                Paragraph(line.prompt or "[No Prompt]", line_style),
                Paragraph(time_data, line_style),
                Paragraph(aux_data_field, line_style),
            ]
        ]

        line_table = Table(
            data=line_table_data,
            colWidths=[inch * 0.75, inch, inch * 3.0, 0.5 * inch, inch * 2.0],
            style=table_style,
        )

        if (line.scene or "[No Scene]") != this_scene:
            this_scene = line.scene or "[No Scene]"
            story.append(
                KeepTogether(
                    [
                        Spacer(1.0, 0.25 * inch),
                        Paragraph("<u>" + this_scene + "</u>", scene_style),
                        line_table,
                    ]
                )
            )
        else:
            line_table.setStyle(table_style)
            story.append(KeepTogether([line_table]))

    return story


def build_tc_data(line: ADRLine, tc_format: TimecodeFormat):
    tc_data = (
        tc_format.seconds_to_smpte(line.start)
        + "<br />"
        + tc_format.seconds_to_smpte(line.finish)
    )
    third_line = []
    if line.reel is not None:
        if line.reel[0:1] == "R":
            third_line.append(f"{line.reel}")
        else:
            third_line.append(f"Reel {line.reel}")
    if line.version is not None:
        third_line.append(f"({line.version})")
    if len(third_line) > 0:
        tc_data = tc_data + "<br/>" + " ".join(third_line)
    return tc_data


def generate_report(
    page_size,
    lines: list[ADRLine],
    tc_rate: TimecodeFormat,
    character_number=None,
    include_omitted=True,
):
    if character_number is not None:
        lines = [r for r in lines if r.character_id == character_number]
        title = f"{lines[0].title} ADR Report ({lines[0].character_name})"
        document_header = f"{lines[0].character_name} ADR Report"
    else:
        title = f"{lines[0].title} ADR Report"
        document_header = "ADR Report"

    if not include_omitted:
        lines = [line for line in lines if not line.omitted]

    lines = sorted(lines, key=lambda line: line.start)

    filename = title + ".pdf"
    doc = make_doc_template(
        page_size=page_size,
        filename=filename,
        document_title=title,
        document_header=document_header,
        title=lines[0].title,
        supervisor=lines[0].supervisor or "",
        client=lines[0].client or "",
        document_subheader=lines[0].spot or "",
        left_margin=0.75 * inch,
    )
    story = build_story(lines, tc_rate)
    doc.build(story)


def output_report(
    lines: list[ADRLine],
    tc_display_format: TimecodeFormat,
    page_size: tuple[float, float] | None = None,
    by_character: bool = False,
):
    if page_size is None:
        page_size = portrait(letter)

    if by_character:
        character_numbers = {r.character_id for r in lines}
        for n in character_numbers:
            generate_report(page_size, lines, tc_display_format, n)
    else:
        generate_report(page_size, lines, tc_display_format)

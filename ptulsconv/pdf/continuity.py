from fractions import Fraction
from typing import Tuple, List

from reportlab.lib.pagesizes import portrait, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table

from ptulsconv.broadcast_timecode import TimecodeFormat
from ptulsconv.pdf import make_doc_template


# TODO: A Continuity

def table_for_scene(scene, tc_format, font_name='Helvetica'):
    scene_style = getSampleStyleSheet()['Normal']
    scene_style.fontName = font_name
    scene_style.leftIndent = 0.
    scene_style.leftPadding = 0.
    scene_style.spaceAfter = 18.

    tc_data = "<em>%s</em><br />%s" % (tc_format.seconds_to_smpte(scene[2]),
                                       tc_format.seconds_to_smpte(scene[3]))

    row = [
        Paragraph(tc_data, scene_style),
        Paragraph(scene[1], scene_style),
    ]

    style = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LEFTPADDING', (0, 0), (0, 0), 0.0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 12.),
             ('FONTNAME', (0, 0), (-1, -1), font_name)]

    return Table(data=[row], style=style, colWidths=[1.0 * inch, 6.5 * inch])


def output_report(scenes: List[Tuple[str, str, Fraction, Fraction]],
                  tc_display_format: TimecodeFormat,
                  title: str, client: str, supervisor, paper_size=letter):
    filename = "%s Continuity.pdf" % title
    document_header = "Continuity"

    doc = make_doc_template(page_size=portrait(paper_size),
                            filename=filename,
                            document_title="Continuity",
                            title=title,
                            client=client,
                            document_subheader="",
                            supervisor=supervisor,
                            document_header=document_header,
                            left_margin=0.5 * inch)
    story = list()
    # story.append(Spacer(height=0.5 * inch, width=1.))
    for scene in scenes:
        story.append(table_for_scene(scene, tc_display_format))

    doc.build(story)

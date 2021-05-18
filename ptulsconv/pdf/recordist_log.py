from reportlab.pdfgen.canvas import Canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

from .common import GRect

import datetime


def output_report(records):
    # order by start

    pass
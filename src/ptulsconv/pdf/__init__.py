import datetime

from reportlab.pdfbase.pdfmetrics import (getAscent, getDescent)
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.platypus.frames import Frame

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from typing import List

# TODO: A Generic report useful for spotting
# TODO: A report useful for M&E mixer's notes
# TODO: Use a default font that doesn't need to be installed

# This is from https://code.activestate.com/recipes/576832/ for
# generating page count messages


class ReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self._report_date = datetime.datetime.now()

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont('Helvetica', 10)  # FIXME make this customizable
        self.drawString(0.5 * inch, 0.5 * inch,
                        "Page %d of %d" % (self._pageNumber, page_count))
        right_edge = self._pagesize[0] - 0.5 * inch
        self.drawRightString(right_edge, 0.5 * inch,
                             self._report_date.strftime("%m/%d/%Y %H:%M"))

        top_line = self.beginPath()
        top_line.moveTo(0.5 * inch, 0.75 * inch)
        top_line.lineTo(right_edge, 0.75 * inch)
        self.setLineWidth(0.5)
        self.drawPath(top_line)
        self.restoreState()


class ADRDocTemplate(BaseDocTemplate):
    def build(self, flowables, filename=None, canvasmaker=ReportCanvas):
        BaseDocTemplate.build(self, flowables, filename, canvasmaker)


def make_doc_template(page_size, filename, document_title,
                      title: str,
                      supervisor: str,
                      document_header: str,
                      client: str,
                      document_subheader: str,
                      left_margin=0.5 * inch,
                      fonts: List[TTFont] = []) -> ADRDocTemplate:
    right_margin = top_margin = bottom_margin = 0.5 * inch
    page_box = GRect(0., 0., page_size[0], page_size[1])
    _, page_box = page_box.split_x(left_margin, direction='l')
    _, page_box = page_box.split_x(right_margin, direction='r')
    _, page_box = page_box.split_y(bottom_margin, direction='u')
    _, page_box = page_box.split_y(top_margin, direction='d')

    footer_box, page_box = page_box.split_y(0.25 * inch, direction='u')
    header_box, page_box = page_box.split_y(0.75 * inch, direction='d')
    title_box, report_box = header_box.split_x(3.5 * inch, direction='r')

    on_page_lambda = (lambda c, _:
                      draw_header_footer(c, report_box, title_box,
                                         footer_box, title=title,
                                         supervisor=supervisor,
                                         document_subheader=document_subheader,
                                         client=client,
                                         doc_title=document_header))

    frames = [Frame(page_box.min_x, page_box.min_y,
                    page_box.width, page_box.height)]

    page_template = PageTemplate(id="Main",
                                 frames=frames,
                                 onPage=on_page_lambda)

    for font in fonts:
        pdfmetrics.registerFont(font)

    doc = ADRDocTemplate(filename,
                         title=document_title,
                         author=supervisor,
                         pagesize=page_size,
                         leftMargin=left_margin, rightMargin=right_margin,
                         topMargin=top_margin, bottomMargin=bottom_margin)

    doc.addPageTemplates([page_template])

    return doc


def time_format(mins, zero_str="-"):
    """
    Formats a duration `mins` into a string
    """
    if mins is None:
        return zero_str
    if mins == 0. and zero_str is not None:
        return zero_str
    elif mins < 60.:
        return "%im" % round(mins)
    else:
        m = round(mins)
        hh, mm = divmod(m, 60)
        return "%i:%02i" % (hh, mm)


def draw_header_footer(a_canvas: ReportCanvas, left_box, right_box,
                       footer_box, title: str, supervisor: str,
                       document_subheader: str, client: str, doc_title="",
                       font_name='Helvetica'):

    (_supervisor_box, client_box,), title_box = \
        right_box.divide_y([16., 16., ])
    title_box.draw_text_cell(a_canvas, title, font_name, 18,
                             inset_y=2., inset_x=5.)
    client_box.draw_text_cell(a_canvas, client, font_name, 11,
                              inset_y=2., inset_x=5.)

    a_canvas.saveState()
    a_canvas.setLineWidth(0.5)
    tline = a_canvas.beginPath()
    tline.moveTo(left_box.min_x, right_box.min_y)
    tline.lineTo(right_box.max_x, right_box.min_y)
    a_canvas.drawPath(tline)

    tline2 = a_canvas.beginPath()
    tline2.moveTo(right_box.min_x, left_box.min_y)
    tline2.lineTo(right_box.min_x, left_box.max_y)
    a_canvas.drawPath(tline2)
    a_canvas.restoreState()

    (doc_title_cell, spotting_version_cell,), _ = \
        left_box.divide_y([18., 14], direction='d')

    doc_title_cell.draw_text_cell(a_canvas, doc_title, font_name, 14.,
                                  inset_y=2.)

    if document_subheader is not None:
        spotting_version_cell.draw_text_cell(a_canvas, document_subheader,
                                             font_name, 12., inset_y=2.)

    if supervisor is not None:
        a_canvas.setFont(font_name, 11.)
        a_canvas.drawCentredString(footer_box.min_x + footer_box.width / 2.,
                                   footer_box.min_y, supervisor)


class GRect:
    def __init__(self, x, y, width, height, debug_name=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.debug_name = debug_name
        self.normalize()

    @property
    def min_x(self):
        return self.x

    @property
    def min_y(self):
        return self.y

    @property
    def max_x(self):
        return self.x + self.width

    @property
    def max_y(self):
        return self.y + self.height

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def normalize(self):
        if self.width < 0.:
            self.width = abs(self.width)
            self.x = self.x - self.width

        if self.height < 0.:
            self.height = abs(self.height)
            self.y = self.y - self.height

    def split_x(self, at, direction='l'):
        if at >= self.width:
            return None, self
        elif at <= 0:
            return self, None
        else:
            if direction == 'l':
                return (GRect(self.min_x, self.min_y, at, self.height),
                        GRect(self.min_x + at, self.y,
                              self.width - at, self.height))
            else:
                return (GRect(self.max_x - at, self.y, at, self.height),
                        GRect(self.min_x, self.y,
                              self.width - at, self.height))

    def split_y(self, at, direction='u'):
        if at >= self.height:
            return None, self
        elif at <= 0:
            return self, None
        else:
            if direction == 'u':
                return (GRect(self.x, self.y, self.width, at),
                        GRect(self.x, self.y + at,
                              self.width, self.height - at))
            else:
                return (GRect(self.x, self.max_y - at, self.width, at),
                        GRect(self.x, self.y,
                              self.width, self.height - at))

    def inset_xy(self, dx, dy):
        return GRect(self.x + dx, self.y + dy,
                     self.width - dx * 2, self.height - dy * 2)

    def inset(self, d):
        return self.inset_xy(d, d)

    def __repr__(self):
        return "<GRect x=%f y=%f width=%f height=%f>" % \
            (self.x, self.y, self.width, self.height)

    def divide_x(self, x_list, direction='l'):
        ret_list = list()

        rem = self
        for item in x_list:
            s, rem = rem.split_x(item, direction)
            ret_list.append(s)

        return ret_list, rem

    def divide_y(self, y_list, direction='u'):
        ret_list = list()

        rem = self
        for item in y_list:
            s, rem = rem.split_y(item, direction)
            ret_list.append(s)

        return ret_list, rem

    def draw_debug(self, a_canvas):
        a_canvas.saveState()
        a_canvas.setFont("Courier", 8)
        a_canvas.rect(self.x, self.y, self.width, self.height)
        a_canvas.drawString(self.x, self.y, self.debug_name or self.__repr__())
        a_canvas.restoreState()

    def draw_border(self, a_canvas, edge):

        def draw_border_impl(en):
            if en == 'min_x':
                coordinates = ((self.min_x, self.min_y),
                               (self.min_x, self.max_y))
            elif en == 'max_x':
                coordinates = ((self.max_x, self.min_y),
                               (self.max_x, self.max_y))
            elif en == 'min_y':
                coordinates = ((self.min_x, self.min_y),
                               (self.max_x, self.min_y))
            elif en == 'max_y':
                coordinates = ((self.min_x, self.max_y),
                               (self.max_x, self.max_y))
            else:
                return

            s = a_canvas.beginPath()
            s.moveTo(*coordinates[0])
            s.lineTo(*coordinates[1])
            a_canvas.drawPath(s)

        if type(edge) is str:
            edge = [edge]

        for e in edge:
            draw_border_impl(e)

    def draw_text_cell(self, a_canvas, text, font_name, font_size,
                       vertical_align='t', force_baseline=None, inset_x=0.,
                       inset_y=0., draw_baseline=False):
        if text is None:
            return

        a_canvas.saveState()

        inset_rect = self.inset_xy(inset_x, inset_y)

        if vertical_align == 'm':
            y = inset_rect.center_y - getAscent(font_name, font_size) / 2.
        elif vertical_align == 't':
            y = inset_rect.max_y - getAscent(font_name, font_size)
        else:
            y = inset_rect.min_y - getDescent(font_name, font_size)

        if force_baseline is not None:
            y = self.min_y + force_baseline

        cp = a_canvas.beginPath()
        cp.rect(self.min_x, self.min_y, self.width, self.height)
        a_canvas.clipPath(cp, stroke=0, fill=0)

        a_canvas.setFont(font_name, font_size)
        tx = a_canvas.beginText()
        tx.setTextOrigin(inset_rect.min_x, y)
        tx.textLine(text)
        a_canvas.drawText(tx)

        if draw_baseline:
            a_canvas.setDash([3.0, 1.0, 2.0, 1.0])
            a_canvas.setLineWidth(0.5)
            bl = a_canvas.beginPath()
            bl.moveTo(inset_rect.min_x, y - 1.)
            bl.lineTo(inset_rect.max_x, y - 1.)
            a_canvas.drawPath(bl)

        a_canvas.restoreState()

    def draw_flowable(self, a_canvas, flowable, inset_x=0.,
                      inset_y=0., draw_baselines=False):
        a_canvas.saveState()

        inset_rect = self.inset_xy(inset_x, inset_y)

        cp = a_canvas.beginPath()
        cp.rect(self.min_x, self.min_y, self.width, self.height)
        a_canvas.clipPath(cp, stroke=0, fill=0)

        w, h = flowable.wrap(inset_rect.width, inset_rect.height)

        flowable.drawOn(a_canvas, inset_rect.x, inset_rect.max_y - h)

        if draw_baselines:
            a_canvas.setDash([3.0, 1.0, 2.0, 1.0])
            a_canvas.setLineWidth(0.5)
            leading = flowable.style.leading

            y = inset_rect.max_y - flowable.style.fontSize - 1.
            while y > inset_rect.min_x:
                bl = a_canvas.beginPath()
                bl.moveTo(inset_rect.min_x, y)
                bl.lineTo(inset_rect.max_x, y)
                a_canvas.drawPath(bl)
                y = y - leading

        a_canvas.restoreState()

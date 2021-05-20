from reportlab.pdfbase.pdfmetrics import (getAscent, getDescent)
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import datetime


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
        self.setFont("Futura", 10)
        self.drawString(0.5 * inch, 0.5 * inch, "Page %d of %d" % (self._pageNumber, page_count))
        right_edge = self._pagesize[0] - 0.5 * inch
        self.drawRightString(right_edge, 0.5 * inch, self._report_date.strftime("%c"))
        top_line = self.beginPath()
        top_line.moveTo(0.5 * inch, 0.75 * inch)
        top_line.lineTo(right_edge, 0.75 * inch)
        self.setLineWidth(0.5)
        self.drawPath(top_line)
        self.restoreState()


def time_format(mins):
    if mins < 60.:
        return "%im" % round(mins)
    else:
        m = round(mins)
        hh, mm = divmod(m, 60)
        return "%ih%im" % (hh, mm)


# draws the title block inside the given rect
def draw_title_block(a_canvas, rect, record):
    (supervisor, client,), title = rect.divide_y([16., 16., ])
    title.draw_text_cell(a_canvas, record['Title'], "Futura", 18, inset_y=2.)
    client.draw_text_cell(a_canvas, record.get('Client', ''), "Futura", 11, inset_y=2.)
    supervisor.draw_text_cell(a_canvas, record.get('Supervisor', ''), "Futura", 11, inset_y=2.)


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
                        GRect(self.min_x + at, self.y, self.width - at, self.height))
            else:
                return (GRect(self.max_x - at, self.y, at, self.height),
                        GRect(self.min_x, self.y, self.width - at, self.height))

    def split_y(self, at, direction='u'):
        if at >= self.height:
            return None, self
        elif at <= 0:
            return self, None
        else:
            if direction == 'u':
                return (GRect(self.x, self.y, self.width, at),
                        GRect(self.x, self.y + at, self.width, self.height - at))
            else:
                return (GRect(self.x, self.max_y - at, self.width, at),
                        GRect(self.x, self.y, self.width, self.height - at))

    def inset_xy(self, dx, dy):
        return GRect(self.x + dx, self.y + dy, self.width - dx * 2, self.height - dy * 2)

    def inset(self, d):
        return self.inset_xy(d, d)

    def __repr__(self):
        return "<GRect x=%f y=%f width=%f height=%f>" % (self.x, self.y, self.width, self.height)

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
                coordinates = ((self.min_x, self.min_y), (self.min_x, self.max_y))
            elif en == 'max_x':
                coordinates = ((self.max_x, self.min_y), (self.max_x, self.max_y))
            elif en == 'min_y':
                coordinates = ((self.min_x, self.min_y), (self.max_x, self.min_y))
            elif en == 'max_y':
                coordinates = ((self.min_x, self.max_y), (self.max_x, self.max_y))
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

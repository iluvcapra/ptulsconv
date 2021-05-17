from reportlab.pdfbase.pdfmetrics import (getAscent, getDescent)


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
            return (GRect(self.min_x, self.min_y, at, self.height),
                    GRect(self.min_x + at, self.y, self.width - at, self.height))

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

    def divide_x(self, x_list, reverse=False):
        ret_list = list()

        rem = self
        for item in x_list:
            s, rem = rem.split_x(item)
            ret_list.append(s)

        return ret_list, rem

    def divide_y(self, y_list, direction='u'):
        ret_list = list()

        rem = self
        for item in y_list:
            s, rem = rem.split_y(item, direction)
            ret_list.append(s)

        return ret_list, rem

    def draw_debug(self, canvas):
        canvas.saveState()
        canvas.setFont("Courier", 8)
        canvas.rect(self.x, self.y, self.width, self.height)
        canvas.drawString(self.x, self.y, self.debug_name or self.__repr__())
        canvas.restoreState()

    def draw_border(self, canvas, edge):

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

            s = canvas.beginPath()
            s.moveTo(*coordinates[0])
            s.lineTo(*coordinates[1])
            canvas.drawPath(s)

        if type(edge) is str:
            edge = [edge]

        for e in edge:
            draw_border_impl(e)

    def draw_text_cell(self, canvas, text, font_name, font_size, vertical_align='t', force_baseline=None, inset_x=0.,
                       inset_y=0., draw_baseline=False):
        canvas.saveState()

        inset_rect = self.inset_xy(inset_x, inset_y)

        if vertical_align == 'm':
            y = inset_rect.center_y - getAscent(font_name, font_size) / 2.
        elif vertical_align == 't':
            y = inset_rect.max_y - getAscent(font_name, font_size)
        else:
            y = inset_rect.min_y - getDescent(font_name, font_size)

        if force_baseline is not None:
            y = self.min_y + force_baseline

        cp = canvas.beginPath()
        cp.rect(self.min_x, self.min_y, self.width, self.height)
        canvas.clipPath(cp, stroke=0, fill=0)

        canvas.setFont(font_name, font_size)
        tx = canvas.beginText()
        tx.setTextOrigin(inset_rect.min_x, y)
        tx.textLine(text)
        canvas.drawText(tx)

        if draw_baseline:
            canvas.setDash([3.0, 1.0, 2.0, 1.0])
            canvas.setLineWidth(0.5)
            bl = canvas.beginPath()
            bl.moveTo(inset_rect.min_x, y - 1.)
            bl.lineTo(inset_rect.max_x, y - 1.)
            canvas.drawPath(bl)

        canvas.restoreState()

    def draw_flowable(self, canvas, flowable, inset_x=0., inset_y=0., draw_baselines=False):
        canvas.saveState()

        inset_rect = self.inset_xy(inset_x, inset_y)

        cp = canvas.beginPath()
        cp.rect(self.min_x, self.min_y, self.width, self.height)
        canvas.clipPath(cp, stroke=0, fill=0)

        w, h = flowable.wrap(inset_rect.width, inset_rect.height)

        flowable.drawOn(canvas, inset_rect.x, inset_rect.max_y - h)

        if draw_baselines:
            canvas.setDash([3.0, 1.0, 2.0, 1.0])
            canvas.setLineWidth(0.5)
            leading = flowable.style.leading

            y = inset_rect.max_y - flowable.style.fontSize - 1.
            while y > inset_rect.min_x:
                bl = canvas.beginPath()
                bl.moveTo(inset_rect.min_x, y)
                bl.lineTo(inset_rect.max_x, y)
                canvas.drawPath(bl)
                y = y - leading

        canvas.restoreState()


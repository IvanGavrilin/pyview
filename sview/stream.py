# The MIT License (MIT)
#
# Copyright (c) 2016 Ivan Gavrilin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import matplotlib.pyplot as plt
import bisect

from matplotlib.ticker import FuncFormatter
from matplotlib.transforms import Bbox

from .line    import Channel as LineChannel
from .scatter import Channel as ScatterChannel
from .text    import Channel as TextChannel
from .dates   import Formatter, Locator

from datetime import datetime, timedelta

AXES_FONT_H = 20.0
AXES_FONT_W = 60.0

def _remove_arg(kw, arg):
    if arg in kw:
        del kw[arg]

class _CustomFmt:
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, x, pos):
        return self.fmt % (x,)

_gid = 1

class AxesProxy:
    def __init__(self, stream, ax):
        self.stream = stream
        self.ax = ax
        self.def_colors = ['#008fd5', '#fc4f30', '#e5ae38', '#6d904f', '#8b8b8b', '#810f7c']  # 538 style
        #self.def_colors = ['#348ABD', '#A60628', '#7A68A6', '#467821', '#D55E00', '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2'] # bmh
        self.cur_color = 0

    def _set_color(self, kw):
        if not 'color' in kw:
            kw['color'] = self.def_colors[self.cur_color]
            self.cur_color = (self.cur_color + 1) % len(self.def_colors)
        elif isinstance(kw['color'], int):
            kw['color'] = self.def_colors[kw['color'] % len(self.def_colors)]

    def add_line(self, name, **kw):
        self._set_color(kw)
        kw['zorder'] = len(self.stream.channels)+1
        return self.stream._create_channel(LineChannel, self.ax, name, **kw)

    def add_scatter(self, name, **kw):
        self._set_color(kw)
        kw['zorder'] = len(self.stream.channels)+1
        return self.stream._create_channel(ScatterChannel, self.ax, name, **kw)

    def add_text_channel(self, name, **kw):
        return self.stream._create_channel(TextChannel, self.ax, name, **kw)

    def add_links_channel(self, name, **kw):
        return self.stream._create_channel(LineChannel, self.ax, name, **kw)


class Stream:

    def create_axes(self):
        return a

    def __init__(self, win, title, time_window):
        self.channels = []
        self.win = win
        self.axes = []
        self.time_window = time_window

        if title:
            self.title_object = self.win.figure.text(0.1, 0.1, title, size='medium', style='italic')
            self.title = title
        else:
            self.title_object = None

        #self.axes[0].xaxis_date(None)
        #self.ly = ax.axvline(color='k')
        self.text_channels = []
        self.last_tm = None
        self.custom_scale_till_time = None

        self.invalidate()

    def _format_coord(self, ax, x, y):
        status = datetime.fromtimestamp(float(x)/1e6).strftime(r"DATE: %Y/%m/%d   %H:%M:%S.%f  ")

        for ch in self.channels:
            if isinstance(ch, LineChannel) or isinstance(ch, ScatterChannel):

                dx = ch.datax
                dy = ch.datay

                i = bisect.bisect_left(dx, x)

                if i < len(dx):
                    status += "  {}: {:7}".format(ch.name, ch.axes.myfmt % (dy[i],))

        return status


    def add_axes(self, fmt, weight = 1.0, width_scale = 1.0):
        global _gid
        if self.axes:
            ax = self.win.figure.add_axes( (0, 0, 0.1, 0.1), gid = str(_gid), sharex = self.axes[0])
        else:
            ax = self.win.figure.add_axes( (0, 0, 0.1, 0.1), gid = str(_gid))
        ax.tick_params(labelsize='small')
        self.axes.append(ax)
        _gid += 1
        ax.links = None

        if len(self.axes) == 1:
            loc = Locator()
            formatter = Formatter(loc)
            self.axes[0].xaxis.set_major_locator(loc)
            self.axes[0].xaxis.set_major_formatter(formatter)

        ax.weight = weight
        ax.stream = self
        ax.width_scale = width_scale

        ax.format_coord = lambda x, y: self._format_coord(ax, x, y)

        ax.yaxis.set_major_formatter(FuncFormatter(_CustomFmt(fmt)))
        ax.myfmt = fmt
        return AxesProxy(self, ax)

    def _create_channel(self, type_v, ax, name, **kw):
        for c in self.channels:
            if c.name == name:
                raise Exception("Channel {} has been added already".format(name))

        channel = type_v(self, ax, **kw)
        channel.name = name
        self.channels.append(channel)
        channel.artist.set_label(name)
        self.invalidate()
        legend = ax.legend(shadow=True, fancybox=True)
        legend.zorder = 100
        legend.get_frame().set_facecolor('#dfdfdf')

        return channel


    def destroy(self):
        for c in self.channels:
            c.destroy()

        for a in self.axes:
            self.win.figure.delaxes(a)

        self.axes = None
        self.channels = None

    def on_zoomed(self):
        if self.title_object:
            self.custom_scale_till_time = datetime.now() + timedelta(0, 30)
            self.title_object.set_text(self.title + " Zoomed")
            self.title_object.set_color('#FF0000')


    def set_position(self, x, y, w, h, abs_w, abs_h):

        top_padding    = AXES_FONT_H/abs_h * 0.15
        right_padding  = AXES_FONT_H/abs_h * 0.15
        bottom_padding = AXES_FONT_H/abs_h

        axes_interval = AXES_FONT_H/abs_h * 0.1

        if self.title_object:
            top_padding += AXES_FONT_H/abs_h * 1.1
            self.title_object.set_position((x + AXES_FONT_W/abs_w * 3, y + (1.0 - AXES_FONT_H/abs_h) * h))

        total_weight = 0.0
        for ax in self.axes:
            total_weight += ax.weight

        first = True
        yc = y + bottom_padding
        for ax in reversed(self.axes):
            left_padding = AXES_FONT_W/abs_w * ax.width_scale
            ax_h = (ax.weight / total_weight) * (h - top_padding - bottom_padding)
            ax.set_position((x + left_padding, yc, w-left_padding-right_padding, ax_h - axes_interval))

            if first:
                first = False
            else:
                for o in ax.xaxis.get_ticklabels():
                    o.set_visible(False)

            clip_box = Bbox(((0, yc*abs_h), (abs_w, (yc + ax_h - axes_interval)*abs_h)))

            for o in ax.yaxis.get_ticklabels():
                o.set_clip_box(clip_box)

            yc += ax_h

        for a in self.axes:
            a.relim()


    def invalidate(self):
        self.dirty = True
        self.win.invalidate()

    def prepare_artists(self):

        changed = False

        if self.dirty:
            for c in self.channels:
                changed = c.prepare_artists() or changed

            self.dirty = False

        if changed:

            for a in self.axes:
                a.relim()

        if not self.custom_scale_till_time or datetime.now() >= self.custom_scale_till_time:
            self.scale_to_default()


    def mouse_move(self, event):
        if self.text_channels:

            xmin = None
            doredraw = False
            for tc in self.text_channels:
                r = tc.mouse_move(event)
                doredraw = r[0] or doredraw

            if doredraw:
                event.canvas.draw()



    def mouse_enter(self, event):
        self.mouse_move(event)



    def mouse_leave(self, event):
        if self.text_channels:
            for tc in self.text_channels:
                tc.mouse_leave(event)

    def set_xrange(self, xmin, xmax):


        axs = {}

        for ch in self.channels:
            if isinstance(ch, LineChannel) or isinstance(ch, ScatterChannel):

                aid = id(ch.axes)
                if aid in axs:
                    axs[aid].append(ch)
                else:
                    axs[aid] = [ch]


        for axes, chs in axs.items():
            first = True
            maxy = 0
            miny = 0

            for ch in chs:
                dx = ch.datax
                dy = ch.datay

                i = bisect.bisect_left(dx, xmin)
                iend = bisect.bisect_right(dx, xmax)

                if i > 0:
                    i-=1

                if iend < len(dx):
                    iend+=1

                while i < iend:

                    if dy[i] is not None:
                        if first:
                            maxy = miny = dy[i]
                            first = False
                        else:
                            maxy = max(maxy, dy[i])
                            miny = min(miny, dy[i])
                    i+=1

            if not first:
                chs[0].axes.set_ylim(miny - (maxy-miny)*0.05, maxy + (maxy-miny)*0.05)

        self.axes[0].set_xlim(xmin, xmax)


    def scale_to_default(self):
        if self.title_object:
            self.custom_scale_till_time = None
            self.title_object.set_text(self.title)
            self.title_object.set_color('#000000')

        if not self.time_window:
            for a in self.axes:
                a.autoscale()
        else:
            dl = self.axes[0].dataLim
            xwidth = self.time_window*1000*1000
            xoff = xwidth * 0.01
            self.axes[0].set_xlim(xmin=dl.x1-xwidth+xoff, xmax=dl.x1+xoff)
            yoff = (dl.y1 - dl.y0) * 0.03
            for a in self.axes:
                a.set_ylim(ymin=dl.y0-yoff, ymax=dl.y1+yoff)

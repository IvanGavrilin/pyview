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
from matplotlib.ticker import FuncFormatter

from .line    import Channel as LineChannel
from .scatter import Channel as ScatterChannel
from .text    import Channel as TextChannel
from .dates   import Formatter, Locator

from datetime import datetime, timedelta

def _remove_arg(kw, arg):
    if arg in kw:
        del kw[arg]

class _CustomFmt:
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, x, pos):
        return self.fmt % (x,)

_gid = 1

class Stream:

    def create_axes(self):
        global _gid
        if self.axes:
            a = self.win.figure.add_axes( (0, 0, 0.1, 0.1), gid = str(_gid), sharex = self.axes[0])
        else:
            a = self.win.figure.add_axes( (0, 0, 0.1, 0.1), gid = str(_gid))
        a.tick_params(labelsize='small')
        _gid += 1
        a.links = None
        return a

    def __init__(self, win, time_window):
        self.channels = dict()
        self.win = win
        self.axes = []
        self.axes.append(self.create_axes())
        self.axes[0].weight = 1.0
        self.axes[0].stream = self
        self.axis_dict = {}
        self.time_window = time_window
        self.title_object = win.figure.text(0.1, 0.1, "Nothing", size='medium', style='italic')
        self.stream_name = 'Nothing'

        loc = Locator()
        formatter = Formatter(loc)
        self.axes[0].xaxis.set_major_locator(loc)
        self.axes[0].xaxis.set_major_formatter(formatter)
        #self.axes[0].xaxis_date(None)
        #self.ly = ax.axvline(color='k')
        self.dirty_layout = True
        self.position = [0, 0, 1, 1]
        self.text_channels = []
        self.last_tm = None
        self.custom_scale_till_time = None

        self.invalidate()

    def _create_channel(self, type_v, name, **kw):
        if name in self.channels:
            del self.channels[name]

        if 'axis' in kw and kw['axis'] in self.axis_dict:

            ax = self.axis_dict[kw['axis']]
            del kw['axis']

            _remove_arg(kw, 'axis_weight')

        elif "axis_weight" in kw:
            self.axes.append(self.create_axes())
            ax = self.axes[-1]
            ax.stream = self
            ax.weight = float(kw["axis_weight"])
            del kw["axis_weight"]

            if "axis" in kw:
                self.axis_dict[kw['axis']] = ax
                del kw['axis']
        else:
            ax = self.axes[0]

        if 'format' in kw:
            ax.yaxis.set_major_formatter(FuncFormatter(_CustomFmt(kw['format'])))
            del kw['format']
        else:
            ax.yaxis.set_major_formatter(FuncFormatter(_CustomFmt("%.f")))

        channel = type_v(self, ax, **kw)
        self.channels[name] = channel
        self.invalidate()
        self.dirty_layout = True
        return channel

    def create_line_channel(self, name, **kw):
        kw['zorder'] = len(self.channels)
        return self._create_channel(LineChannel, name, **kw)

    def create_scatter_channel(self, name, **kw):
        kw['zorder'] = len(self.channels)
        return self._create_channel(ScatterChannel, name, **kw)

    def create_text_channel(self, name, **kw):
        t = self._create_channel(TextChannel, name, **kw)
        self.text_channels.append(t)
        return t

    def create_links_channel(self, name, **kw):
        t = self._create_channel(LinksChannel, name, **kw)
        return t

    def destroy(self):
        for c in self.channels:
            c.destroy()

        for a in self.axes:
            self.win.figure.delaxes(a)

        self.axes = None
        self.channels = None

    def set_name(self, txt):
        self.title_object.set_text(txt)
        self.stream_name = txt

    def on_zoomed(self):
        self.custom_scale_till_time = datetime.now() + timedelta(0, 30)
        self.title_object.set_text(self.stream_name + " Zoomed")
        self.title_object.set_color('#FF0000')


    def set_position(self, x, y, w, h):

        w1 = w * 0.9
        h1 = h * 0.9
        x1 = x + (w - w1) * 0.5
        y1 = y + (h - h1) * 0.5

        new_pos = (x1, y1, w1, h1)

        if new_pos != self.position:
            self.position = new_pos
            self.dirty_layout = True

        self.title_object.set_position((x + 0.01 * w, y + h - 0.03 * h))


    def invalidate(self):
        self.dirty = True
        self.win.invalidate()

    def prepare_artists(self):

        changed = False

        if self.dirty_layout:

            total_weight = 0.0
            for ax in self.axes:
                total_weight += ax.weight

            yc = self.position[1]
            for ax in reversed(self.axes):
                h = ax.weight * self.position[3] / total_weight
                ax.set_position((self.position[0], yc + h*0.005, self.position[2], h*0.99))
                #ax.autoscale()
                yc += h

            self.dirty_layout = False
            changed = True

        if self.dirty:
            for c in self.channels.values():
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


    def scale_to_default(self):
        self.custom_scale_till_time = None
        self.title_object.set_text(self.stream_name)
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

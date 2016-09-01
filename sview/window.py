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

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as anim

import datetime

mpl.rcParams['axes.facecolor'] = '#d3d3d3'
mpl.rcParams['axes.edgecolor'] = '#303030'
mpl.rcParams['axes.grid'] = 'True'
mpl.rcParams['grid.color'] = '#323232'
mpl.rcParams['grid.linewidth'] = 0.5
mpl.rcParams['patch.facecolor'] = 'blue'
mpl.rcParams['patch.edgecolor'] = '#eeeeee'
mpl.rcParams['figure.facecolor'] = '#e3e3e3'
mpl.rcParams['font.family'] = 'sans-serif'
#plt.style.use('fivethirtyeight')


from .stream import Stream

class _MyAnim(anim.FuncAnimation):
    def __init__(self, fig, updater, interval, arg):
        self.run = 0
        self.updater = updater
        self.arg = arg
        super(_MyAnim, self).__init__(fig, lambda x: updater.update(arg), interval=interval, repeat=True)

    def _step(self, *args):
        if self.updater.is_update_needed(self.arg):
            super(_MyAnim, self)._step(*args)


_all_windows = []

class Window:
    def draw_event(self, event):
        print("draw_event")

    def __init__(self, title = 'Figure 1', updater = None):
        self.figure = plt.figure()
        self.streams = []
        self.dirty = True
        _all_windows.append(self)

        #self.figure.canvas.mpl_connect('draw_event',     self.draw_event)
        self.figure.canvas.mpl_connect('axes_enter_event',     self.mouse_enter)
        self.figure.canvas.mpl_connect('axes_leave_event',     self.mouse_leave)
        self.figure.canvas.mpl_connect('motion_notify_event',  self.mouse_move)
        self.figure.canvas.mpl_connect('scroll_event',         self.mouse_wheel)

        #self.figure.canvas.mpl_connect('button_press_event',   self.button_press)
        self.figure.canvas.mpl_connect('button_release_event', self.button_release)

        self.figure.canvas.mpl_connect('key_press_event',      self.key_press)
        #self.figure.canvas.mpl_connect('key_release_event',    self.key_release)

        self.figure.canvas.mpl_connect('resize_event',      self.resize_event)

        self.figure.canvas.set_window_title(title)

        if updater:
            self.a = _MyAnim(self.figure, updater, interval=300, arg=self)
        #if anim_func:
        #    self.a = anim.FuncAnimation(self.figure, _ClosureWithArg(anim_func, self), frames=1, interval=200, repeat=True)


    def create_stream(self, title = None, updater = None, time_window = None):

        s = Stream(self, title, time_window)
        self.streams.append(s)
        self.dirty = True

        if updater:
            s.a = _MyAnim(self.figure, updater, interval=200, arg=s)
            #s.a = anim.FuncAnimation(self.figure, _ClosureWithArg(anim_func, s), frames=1, interval=200, repeat=True) #, blit=True)

        return s

    def destroy_stream(self, s):
        self.dirty = True
        self.streams.remove(s)
        s.destroy()

    def invalidate(self):
        self.dirty = True

    def _calc_layout(self, streams, x, y, w, h, abs_w, abs_h):
        if len(streams) > 3:
            half = len(streams) // 2
            if h >= w*0.9:
                self._calc_layout(streams[0:half], x, y+h/2, w, h/2, abs_w, abs_h)
                self._calc_layout(streams[half:], x, y, w, h/2, abs_w, abs_h)
            else:
                self._calc_layout(streams[0:half], x, y, w/2, h, abs_w, abs_h)
                self._calc_layout(streams[half:], x+w/2, y, w/2, h, abs_w, abs_h)
        else:
            if len(streams) == 1:
                streams[0].set_position(x, y, w, h, abs_w, abs_h)
            elif len(streams) == 2:
                streams[0].set_position(x,     y, w/2, h, abs_w, abs_h)
                streams[1].set_position(x+w/2, y, w/2, h, abs_w, abs_h)
            elif len(streams) == 3:
                streams[0].set_position(x,       y, w/3, h, abs_w, abs_h)
                streams[1].set_position(x+w/3,   y, w/3, h, abs_w, abs_h)
                streams[2].set_position(x+w*2/3, y, w/3, h, abs_w, abs_h)


    def prepare_artists(self):

        #print("win.invalidate, ", self.dirty)
        if self.dirty:

            for s in self.streams:
                s.prepare_artists()

            self.dirty = False


    def mouse_move(self, event):
        if event.inaxes and event.inaxes.stream:
            event.inaxes.stream.mouse_move(event)



    def mouse_enter(self, event):
        if not event.inaxes:
            return

        if event.inaxes.stream:
            event.inaxes.stream.mouse_enter(event)

    def mouse_leave(self, event):

        if event.inaxes.stream:
            event.inaxes.stream.mouse_leave(event)

    def mouse_wheel(self, event):
        if event.inaxes:

            axis = event.inaxes.xaxis
            pos  = event.xdata

            vmin, vmax = axis.get_view_interval()
            interval = abs(vmax - vmin)
            k = 0.2
            if event.button == 'down':
                delta = interval * k
            else:
                delta = interval * k / (1.0 + k) * -1.0

            #print("delta", delta, "vmin", vmin, "vmax", vmax)

            l1 = abs(pos - vmin) / interval
            vmin = vmin + l1 * delta
            vmax = vmax - (1.0 - l1) * delta

            if event.inaxes.stream:
                event.inaxes.stream.on_zoomed()
                event.inaxes.stream.set_xrange(vmin, vmax)

            event.canvas.draw()

            #print(event.inaxes.xaxis.get_view_interval(), event.ydata, event.button, event.key)
        pass

    def button_release(self, event):
        #print('button release', event.button, event.xdata)
        if event.button == 2:
            if event.inaxes and event.inaxes.links:
                event.inaxes.links.open(event)

    def resize_event(self, event):
        #print("resize_event", event.width, event.height)
        self._calc_layout(self.streams, 0.0, 0.0, 1.0, 1.0, event.width, event.height)


    def key_press(self, event):

        if event.inaxes and event.inaxes.stream:
            if event.key == 'h':
                event.inaxes.stream.scale_to_default()
                event.canvas.draw()
            elif event.key == ' ':
                event.inaxes.links.open(event)


def event_loop():
    print("Use backend:", mpl.get_backend())
    for w in _all_windows:
        w.prepare_artists()
    plt.show()



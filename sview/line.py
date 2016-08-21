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

from matplotlib.lines import Line2D
import datetime

# Set the marker fill style
# fillstyle: ['full' | 'left' | 'right' | 'bottom' | 'top' | 'none']
# drawstyle: [ 'default' | 'steps' | 'steps-pre' | 'steps-mid' | 'steps-post' ]
# linestyle: [ '-' | '--' | '-.' | ':' | 'None' | ' ' | '' ]

_SUPPORTED_ARGS = dict(drawstyle=1, marker=1, markersize=1, linestyle=1, linewidth=1, color=1, alpha=1, fillstyle=1, zorder=1)
_FLOAT_ARGS = dict(markersize=1, alpha=1, linewidth=1)

class Channel:
    def __init__(self, stream, ax, **kw):
        self.stream = stream
        self.dirty = True
        self.datax = []
        self.datay = []
        self.axes = ax

        self.repeat = False
        self.last_tm = None

        args = {}
        for k, v in kw.items():
            if k == 'repeat':
                self.repeat = bool(v)
            elif not k in _SUPPORTED_ARGS:
                raise Exception("Line: unknown arg '{}'".format(k))
            elif k in _FLOAT_ARGS:
                args[k] = float(v)
            else:
                args[k] = v

        self.artist = Line2D(self.datax, self.datay, **args)
        self.axes.add_line(self.artist)


    def prepare_artists(self):
        stream = self.stream

        if not self.dirty and self.last_tm == stream.last_tm:
            return False

        self.last_tm = stream.last_tm

        if self.repeat and self.datax[-1] != stream.last_tm:
            self.artist.set_data(self.datax + [stream.last_tm], self.datay + [self.datay[-1]])
        else:
            self.artist.set_data(self.datax, self.datay)

        self.dirty = False
        return True


    def destroy(self):
        if self.artist:
            self.axes.lines.remove(self.artist)

        self.artist = None
        self.stream = None

    def update_from_str(self, tm, line):
        self.dirty = True

        if line is not None:
            new_value = float(line)
        else:
            new_value = line

        if isinstance(tm, datetime.datetime):
            tm = tm.timestamp() * 1e6

        dx = self.datax
        dy = self.datay

        if len(dx) > 1 and dy[-1] == dy[-2] and dy[-1] == new_value:
            dx[-1] = tm
        else:
            dx.append(tm)
            dy.append(new_value)

        self.stream.invalidate()



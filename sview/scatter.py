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

# marker: see MPL doc

_SUPPORTED_ARGS = dict(marker=1, size=1, color=1, alpha=1, zorder=1)
_FLOAT_ARGS = dict(alpha=1, size=1)

class Channel:
    def __init__(self, stream, ax, **kw):
        self.stream = stream
        self.dirty = True
        self.datax = []
        self.datay = []
        self.axes = ax

        args = {}
        for k, v in kw.items():
            if not k in _SUPPORTED_ARGS:
                raise Exception("Scatter: unknown arg '{}'".format(k))
            if k in _FLOAT_ARGS:
                if k == 'size':
                    args['s'] = float(v) * float(v)
                else:
                    args[k] = float(v)
            else:
                args[k] = v

        self.artist = self.axes.scatter(self.datax, self.datay, **args)


    def prepare_artists(self):
        if not self.dirty:
            return False

        self.artist.set_offsets(list(zip(self.datax, self.datay)))

        self.dirty = False
        self.axes.relim()
        return True


    def destroy(self):
        if self.artist:
            self.artist.remove()

        self.artist = None
        self.stream = None

    def update_from_str(self, tm, line):
        self.dirty = True
        self.datax.append(tm)
        self.datay.append(float(line))
        self.stream.invalidate()



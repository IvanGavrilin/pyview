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

_SUPPORTED_ARGS = dict(size=1, color=1, alpha=1, zorder=1)
_FLOAT_ARGS = dict(alpha=1, size=1)

class Channel:
    def __init__(self, stream, ax, **kw):
        self.stream = stream
        self.dirty = True
        self.datatm = []
        self.data = []
        self.axes = ax

        args = {}
        for k, v in kw.items():
            if not k in _SUPPORTED_ARGS:
                #raise Exception("Line: unknown arg '{}'".format(k))
                continue
            if k in _FLOAT_ARGS:
                args[k] = float(v)
            else:
                args[k] = str(v)

        self.props = args


    def prepare_artists(self):
        if not self.dirty:
            return False

        if self.data:
            self.axes.set_title(self.data[-1], **self.props)

        self.dirty = False
        return True


    def destroy(self):
        self.axes.set_title('')
        self.stream = None

    def update_from_str(self, tm, line):
        self.dirty = True
        self.datatm.append(tm)
        self.data.append(line)
        self.stream.invalidate()

    def _update_text(self, text, text_tm):
        old_title = self.axes.get_title()
        if old_title != text:
            self.axes.set_title(text, **self.props)
            return (True, text_tm)
        return (False, )

    def mouse_move(self, event):
        for i in range(len(self.datatm)-1, -1, -1):
            if event.xdata >= self.datatm[i]:
                return self._update_text(self.data[i], self.datatm[i])

        return self._update_text('', None)

    def mouse_leave(self, event):
        return self._update_text(self.data[-1], None)

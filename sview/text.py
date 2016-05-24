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

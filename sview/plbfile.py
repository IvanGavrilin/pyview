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

from collections import OrderedDict
from datetime import datetime
import os

def _unpack_args(rest_line):
    args = {}
    for a in rest_line:
        if len(a) > 1:
            name, _, value = a.partition('=')
            args[name] = value

    return args

def isplit(source, sep):
    sepsize = len(sep)
    start = 0
    while True:
        idx = source.find(sep, start)
        if idx == -1:
            yield source[start:]
            return
        yield source[start:idx]
        start = idx + sepsize


# Returns last pos in the file
def load_stream(stream, filename, seek_to_pos=None):

    nlines = 0

    stream.last_tm = None
    stream.basedir = os.path.dirname(os.path.abspath(filename))

    with open(filename) as fp:

        if seek_to_pos:
            fp.seek(seek_to_pos)

        for line in fp:

            ar = line.split(";")

            ar_len = len(ar)
            if ar_len < 4:
                if ar_len == 3:
                    ar.append('')
                else:
                    continue

            nlines += 1

            line_type = ar[0]

            if line_type == 'a':

                ar = line.rstrip().split(";")

                channel_name = ar[1]
                channel_type = ar[2]

                if not channel_name in stream.channels:
                    if channel_type == 'line':
                        stream.create_line_channel(channel_name, **_unpack_args(ar[3:]))
                    elif channel_type == 'scatter':
                        stream.create_scatter_channel(channel_name, **_unpack_args(ar[3:]))
                    elif channel_type == 'text':
                        stream.create_text_channel(channel_name, **_unpack_args(ar[3:]))
                    else:
                        raise Exception("Unknown channel type '{}'".format(channel_type))
                        continue

            elif line_type == 'v':
                channel_name = ar[2]
                c = stream.channels.get(channel_name, None)
                if not c:
                    print("Error: unknown channel_name(", channel_name, ") in line: ", line)
                else:

                    #c.update_from_str(int(ar[1]), ';'.join(ar[3:]))
                    cur_tm = int(ar[1])
                    if ar_len == 4: # Performance optimisation
                        c.update_from_str(cur_tm, ar[3])
                    else:
                        c.update_from_str(cur_tm, line[len(ar[0])+len(ar[1])+len(ar[2])+3:])

                    if stream.last_tm:
                        stream.last_tm = max(stream.last_tm, cur_tm)
                    else:
                        stream.last_tm = cur_tm

        if nlines > 0:
            str_tm1 = datetime.fromtimestamp(float(stream.last_tm)/1e6).strftime(r"<%Y/%m/%d %H:%M:%S.%f>")
            str_tm2 = datetime.now().strftime(r"<%Y/%m/%d %H:%M:%S.%f>")
            print("Loaded", nlines, "lines at ", str_tm1, " for", str_tm2)
        return fp.tell()

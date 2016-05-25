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

import math
import numpy as np

from datetime import datetime

_WEEKDAYS = "Sun|Mon|Tue|Wed|Thu|Fri|Sat".split("|")
_MOSCOW_TZ_OFFSET = 4 * 60 * 60 * 1000 * 1000

class Formatter:
    axis = None

    def set_axis(self, axis):
        self.axis = axis

    def __init__(self, loc):
        self.locator = loc

    def __call__(self, x, pos=None):

        if pos is None:
            return datetime.fromtimestamp(float(x)/1e6).strftime(r"  DATE:  %Y/%m/%d   %H:%M:%S.%f     ")

        if x < 20:
            return "--"

        width = self.axis.axes.transAxes.transform_point((1, 1))[0] - self.axis.axes.transAxes.transform_point((0, 0))[0]

        if width > 500 or (pos % 2) == 1:
            return self.locator.fmt(x)
        return ''

        if pos:
            return "{}\ntest".format(x)
        return str(x)

    def format_data(self, value):
        return self.__call__(value)

    def format_data_short(self, value):
        return self.format_data(value)

    def get_offset(self):
        return ''

    def set_locs(self, locs):
        self.locs = locs


def fmt_sec(value):  return "%ds" % ((int(value)/1000000)%60,)
def fmt_secf(value): return "%.1fs" % (((int(value)/100000)%600)*0.1,)

def fmt_ms(value):  return "%dms" % ((int(value)/1000)%1000,)
def fmt_msf(value):  return "%.1fms" % (((int(value)/100)%10000)*0.1,)

def fmt_def(value): return str(value)
def fmt_ns(value):  return "%dns" % (int(value) % 1000,)

def fmt_hms(value):
    return datetime.fromtimestamp(float(value)/1e6).strftime("%H:%M:%Ss")

def fmt_hm(value):
    return datetime.fromtimestamp(float(value)/1e6).strftime("%H:%M")

def fmt_wdhm(value):
    dt = datetime.fromtimestamp(float(value)/1e6)
    return _WEEKDAYS[dt.weekday()] + dt.strftime(" %H:%M")

def fmt_mdwd(value):
    dt = datetime.fromtimestamp(float(value)/1e6)
    return dt.strftime("%m/%d ") + _WEEKDAYS[dt.weekday()]

def fmt_ymd(value):
    dt = datetime.fromtimestamp(float(value)/1e6)
    return dt.strftime("%Y/%m/%d")

def fmt_y(value):
    dt = datetime.fromtimestamp(float(value)/1e6)
    return dt.strftime("%Y")


_step_limits= [
    (1, fmt_ns),
    (2, fmt_ns),
    (5, fmt_ns),
    (2*10, fmt_ns),
    (5*10, fmt_ns),
    (1*100, fmt_msf),
    (2*100, fmt_msf),
    (5*100, fmt_msf),
    (1*1000, fmt_ms),
    (2*1000, fmt_ms),
    (5*1000, fmt_ms),
    (1*10000, fmt_ms),
    (2*10000, fmt_ms),
    (5*10000, fmt_ms),
    (1*100000, fmt_secf),
    (2*100000, fmt_secf),
    (5*100000, fmt_secf),

    (1*1000000, fmt_hms),
    (2*1000000, fmt_hms),
    (3*1000000, fmt_hms),
    (5*1000000, fmt_hms),
    (6*1000000, fmt_hms),
    (10*1000000, fmt_hms),
    (15*1000000, fmt_hms),
    (20*1000000, fmt_hms),
    (30*1000000, fmt_hms),

    (1*60*1000000, fmt_hm),
    (2*60*1000000, fmt_hm),
    (3*60*1000000, fmt_hm),
    (5*60*1000000, fmt_hm),
    (6*60*1000000, fmt_hm),
    (10*60*1000000, fmt_hm),
    (15*60*1000000, fmt_hm),
    (20*60*1000000, fmt_hm),
    (30*60*1000000, fmt_hm),
    (60*60*1000000, fmt_hm),
    (2*60*60*1000000, fmt_hm),
    (3*60*60*1000000, fmt_hm),
    (4*60*60*1000000, fmt_hm),
    (6*60*60*1000000, fmt_wdhm),
    (8*60*60*1000000, fmt_wdhm),
    (12*60*1000000, fmt_wdhm),
    (24*60*60*1000000, fmt_mdwd),
    (2*24*60*60*1000000, fmt_mdwd),
    (4*24*60*60*1000000, fmt_mdwd),
    (7*24*60*60*1000000, fmt_ymd),
    (10*24*60*60*1000000, fmt_ymd),
    (15*24*60*60*1000000, fmt_ymd),
    (20*24*60*60*1000000, fmt_ymd),
    (30*24*60*60*1000000, fmt_ymd),
    (60*24*60*60*1000000, fmt_ymd),
    (100*24*60*60*1000000, fmt_ymd),
    (150*24*60*60*1000000, fmt_ymd),
    (200*24*60*60*1000000, fmt_ymd),
    (300*24*60*60*1000000, fmt_ymd),
    (365*24*60*60*1000000, fmt_y),
]

class Locator:

    axis = None

    def set_axis(self, axis):
        self.axis = axis

    def __call__(self):
        #print("NullLocator::__call__(): axis {}".format(self.axis))
        vmin, vmax = self.axis.get_view_interval()
        return self.tick_values(vmin, vmax)

    def view_limits(self, vmin, vmax):
        return (vmin, vmax)

    def autoscale(self):
        pass

    def refresh(self):
        """refresh internal information based on current lim"""
        #print("NullLocator::refresh()")
        pass


    def tick_values(self, vmin, vmax):
        num = 10
        step = (vmax - vmin) / num

        #print("step ", step)

        self.fmt = fmt_def
        for i in range(len(_step_limits)):
            if step <= _step_limits[i][0]:
                self.fmt = _step_limits[i][1]

                rstep = _step_limits[i][0]

                ivmin = int(vmin) + _MOSCOW_TZ_OFFSET
                start = ivmin - (ivmin % rstep) - _MOSCOW_TZ_OFFSET

                #print("rstep ", rstep)

                loc = []

                while start < vmax:
                    loc.append(start)
                    start = start + rstep

                return loc

        step_seconds = step / 1e6

        v = [i for i in range(num)]

        print(v)

        #self.data
        return v



__all__ = ('Formatter', 'Locator',)

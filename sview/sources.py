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

import datetime
import traceback
import random

class RandomUpdater:
    def __init__(self):
        self.limit = 0.2
        self.initialized = False

    def is_update_needed(self, stream):
        if not self.initialized:
            return True
        if random.random() < self.limit:
            return True
        return False

    def update(self, stream):
        try:
            if not self.initialized:
                self.initialized = True
                self.sig_a = stream.create_line_channel("sig_a", color="#6699CC", drawstyle='steps-pre', axis='top', axis_weight=0.8)
                self.sig_b = stream.create_line_channel("sig_b", color="#DD3477", drawstyle='steps-pre', axis='top', axis_weight=0.8, fillstyle='bottom')

            now = datetime.datetime.now().timestamp() * 1e6
            self.sig_a.update_from_str(now, random.random())
            self.sig_b.update_from_str(now, random.random())

        except Exception as e:
            print("Exception: ", e)
            print("======================================================================================")
            print(traceback.format_exc())
            print("======================================================================================")

        stream.win.prepare_artists()

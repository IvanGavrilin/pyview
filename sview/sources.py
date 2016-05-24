from os import stat
import subprocess
import datetime
import traceback
import sys
from glob import glob
from os import path

from .plbfile import load_stream

class FileUpdater:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pos = 0
        self.st_mtime = None
        self.st_mtime_ns = None

    def is_update_needed(self, stream):
        s = stat(self.filepath)
        if s.st_mtime != self.st_mtime or s.st_mtime_ns != self.st_mtime_ns:
            self.st_mtime = s.st_mtime
            self.st_mtime_ns = s.st_mtime_ns
            return True
        return False

    def update(self, stream):
        try:
            self.pos = load_stream(stream, self.filepath, self.pos)
        except Exception as e:
            print("Exception: ", e)
            print("======================================================================================")
            print(traceback.format_exc())
            print("======================================================================================")

        stream.win.prepare_artists()

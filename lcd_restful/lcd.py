# coding=utf-8
from __future__ import print_function
from RPLCD import CharLCD
from RPi.GPIO import BCM
import sys
if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

from .codec import encode_char


class Lcd(CharLCD):
    def __init__(self, fake=False):
        super(Lcd, self).__init__(
            rows=4,
            cols=20,
            numbering_mode=BCM,
            pin_rs=25,    # 4
            pin_rw=None,  # 5
            pin_e=24,     # 6
            pins_data=[
                23,   # d4 11
                17,   # d5 12
                21,   # d6 13
                22],  # d7 14
            pin_backlight=None,
            auto_linebreaks=False)

    # For Adafruit lib compat
    def message(self, msg, as_ordinal=False, autowrap=False, clear=False):
        if clear:
            self.clear()
        if as_ordinal:
            return self.write_raw(msg)
        self.write_utf(msg, autowrap)

    def write_utf(self, msg, autowrap=False):
        for utfc in msg:
            if utfc == '\n':
                self.row_inc(keep_col=True)
            elif utfc == '\r':
                row, _ = self.cursor_pos
                self.cursor_pos = (row, 0)
            else:
                self.write(encode_char(utfc))
                if autowrap:
                    row, col = self.cursor_pos
                    if col >= self.lcd.cols:
                        self.row_inc()

    def write_raw(self, msg):
        if not isinstance(msg, list):
            msg = [msg]
        for line in msg:
            for b in line:
                # if line is a byte array, instead of list of 8b ints
                if isinstance(b, binary_type):
                    b = ord(b)
                self.write(b)
            self.row_inc()

    def row_inc(self, keep_col=False):
        row, col = self.cursor_pos
        if not keep_col:
            col = 0
        if row < self.lcd.rows - 1:
            self.cursor_pos = (row + 1, col)
        else:
            self.cursor_pos = (0, col)


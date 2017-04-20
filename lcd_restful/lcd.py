from RPLCD import CharLCD

from . import ON_RPI, patch_fake_gpio, inject_hw
from .codec import encode_char


class Lcd(CharLCD):
    def __init__(self, fake=False):
        if fake and ON_RPI:
            patch_fake_gpio()
        if fake or not ON_RPI:
            inject_hw()
        super(Lcd, self).__init__(
            rows=4,
            cols=20,
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


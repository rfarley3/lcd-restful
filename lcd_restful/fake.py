# from RPLCD.common import (
#     LCD_MOVERIGHT,
# )
from .codec import hitachi_utf_map
LCD_MOVERIGHT = 0x04


class FakesException(BaseException):
    pass


class HwException(FakesException):
    pass


class Hw(object):
    def __init__(self, rows=4, cols=20, raise_on_unknown=True, compact=True):
        self.raise_unk = raise_on_unknown
        self.reuse = compact  # re-use term output (clear before each print)
        self.initialized = False
        self.pin_map = {
            'd4': 23,
            'd5': 17,
            'd6': 21,
            'd7': 22,
            'rs': 25,
            'en': 24}
        self.pins = {}
        self.read_width = 4
        # Hw detects width during cmd based initialization
        # however, this object needs to know width before init
        self.init_cnt = 4
        if 'd0' in self.pin_map:
            self.init_cnt = 3
            self.read_width = 8
        self.write4_1 = True
        self.has_outputted = False
        self.rows = rows
        self.cols = cols
        self.row_offsets = [0x00, 0x40, self.cols, 0x40 + self.cols]
        self.decode_map = hitachi_utf_map()
        self.init_charcells()

    def __repr__(self):
        return '%s(rows=%s,cols=%s)' % (self.__class__.__name__, self.rows, self.cols)

    # override if output type changes (like a file)
    def __str__(self):
        lcd_str = ''
        lcd_str += '-' * (self.cols + 2) + '\n'
        for r in range(self.rows):
            r_str = '-'
            for c in range(self.cols):
                r_str += self.cells[r].get(c, ' ')
            lcd_str += r_str + '-\n'
        lcd_str += '-' * (self.cols + 2)
        return lcd_str

    # override if output type changes (like a file)
    def out_clear(self):
        """Erase terminal screen area"""
        tot_r = self.rows + 2
        tot_c = self.cols + 2
        for r in range(tot_r):
            print('\b' * tot_c, end='')
            # + 5 to handle when wide chars make box larger
            print(' ' * (tot_c + 5), end='')
            print('\b' * 5, end='')
            print('\033[A', end='')
        print('\b' * tot_c, end='')

    # override if output type changes (like a file)
    def out_draw(self):
        """Output matrix of chars to terminal screen area"""
        print(self)

    def out_refresh(self):
        # TODO allow refreshing single cells, or range of cells
        if self.has_outputted and self.reuse:
            self.out_clear()
        self.out_draw()
        self.has_outputted = True

    def _set(self, pin, value):
        """Gpio.output/_set will call this to give HW a trigger to read"""
        # only handles a bool value
        old_val = self.pins.get(pin)
        self.pins[pin] = value
        if pin == self.pin_map['en']:
            if old_val is 0 and value is 1:
                self.read()

    def read(self):
        d7 = self.get_pin('d7')
        d6 = self.get_pin('d6')
        d5 = self.get_pin('d5')
        d4 = self.get_pin('d4')
        half_word = (d7 << 3 | d6 << 2 | d5 << 1 | d4)
        if self.read_width == 4:
            self.write4(half_word)
            return
        # if read_width == 8, get full word
        d3 = self.get_pin('d3')
        d2 = self.get_pin('d2')
        d1 = self.get_pin('d1')
        d0 = self.get_pin('d0')
        lower_word = (d3 << 3 | d2 << 2 | d1 << 1 | d0)
        full_word = half_word | lower_word
        self.write8(full_word)

    def get_pin(self, name):
        pin_num = self.pin_map.get(name)
        if pin_num is None:
            return 0
        return self.pins.get(pin_num, 0)

    def write4(self, half_word):
        """We get 4b at a time, combine each pair for 8b"""
        if self.write4_1:
            self.upper = half_word << 4
            self.write4_1 = False
            return
        full_word = self.upper | half_word
        self.write4_1 = True
        self.upper = None
        self.write8(full_word)

    def write8(self, full_word):
        # If RS is HIGH, then it is a char, else command
        if self.pins[self.pin_map['rs']]:
            self.write8_chr(full_word)
        elif not self.initialized:
            self.initialize(full_word)
        else:
            self.write8_cmd(full_word)

    def initialize(self, val):
        if val not in [0x03, 0x30, 0x02]:
            raise HwException('Invalid cmd based init insn, is API odd?')
        self.init_cnt -= 1
        if self.init_cnt == 0:
            self.initialized = True

    def write8_chr(self, char_val):
        # import sys
        # print('write_at %s %s\n' % (self.cur_c, self.cur_r), file=sys.stderr)
        mapped_char = self.decode_map.get(char_val)
        self.cells[self.cur_r][self.cur_c] = mapped_char
        # it appears that the LCD increments its cursor per char
        # unknown how it handles when max col is reached
        self.cur_c += 1
        self.out_refresh()

    def write8_cmd(self, val):
        # LCD_CLEARDISPLAY
        if val == 1:
            return self.clear()
        # LCD_SETDDRAMADDR
        elif val >> 7 == 1:
            # Set cursor pos
            return self.cursor(val & 0b01111111)
        # LCD_SETCGRAMADDR
        elif (val >> 6) & 0x01 == 1:
            # Add a custom symbol/char
            return self.unhandled_cmd(val)  # TODO
        # LCD_FUNCTIONSET
        elif (val >> 5) & 0x01 == 1:
            # sets write bit width
            # return self.unhandled_cmd(val)
            return self.funcset(val & 0b00011111)
        # LCD_CURSORSHIFT
        elif (val >> 4) & 0x01 == 1:
            # LCD_DISPLAYMOVE
            if (val >> 3) & 0x01 == 1:
                # auto move all text on screen one direction
                return self.move((val & 0b00000111) == LCD_MOVERIGHT)
            return self.unhandled_cmd(val)
        # LCD_DISPLAYCONTROL
        elif (val >> 3) & 0x01 == 1:
            # turn on and off display, show cursor, blink cursor
            return self.displayset(val & 0b00000111)
        # LCD_ENTRYMODESET
        elif (val >> 2) & 0x01 == 1:
            # set which way text enters, sets autoscroll
            # NOTE assumes ENTRYLEFT
            return self.entryset(val & 0b00000011)
        # LCD_RETURNHOME
        elif (val >> 1) & 0x01 == 1:
            return self.set_cursor(0, 0)
        raise HwException('Unexpected command value')

    def unhandled_cmd(self, arg):
        if self.raise_unk:
            raise HwException('Unhandled, but known, cmd %s' % arg)

    def init_charcells(self):
        self.cur_c = 0
        self.cur_r = 0
        self.cells = {}
        for r in range(self.rows):
            self.cells[r] = {}
            # get(, ' ') allows us to skip setting all to ' '

    def clear(self, *args):
        self.init_charcells()
        self.out_refresh()

    def set_cursor(self, col, row):
        # import sys
        # print('set_cursor %s %s\n' % (col, row), file=sys.stderr)
        self.cur_c = col
        self.cur_r = row

    def cursor(self, arg):
        # Per Adafruit_CharLCD.LCD_ROW_OFFSETS usage:
        # LCD_SETDDRAMADDR | (col + LCD_ROW_OFFSETS[row]))
        # LCD_ROW_OFFSETS = (0x00, 0x40, 0x14, 0x54)
        ros = self.row_offsets
        if arg >= ros[3]:
            return self.set_cursor(arg - ros[3], 3)
        elif arg < ros[2]:
            return self.set_cursor(arg - ros[0], 0)
        elif arg >= ros[1]:
            return self.set_cursor(arg - ros[1], 1)
        elif arg >= ros[2]:
            return self.set_cursor(arg - ros[2], 2)
        else:
            raise HwException('Bad cursor pos %s' % arg)

    def funcset(self, arg):
        # self.read_width = 4
        if arg & 0x10 == 0x10:
            self.read_width = 8
        self.two_line = True
        if arg & 0x08 != 0x08:
            # 1LINE
            self.two_line = False
            raise HwException('Unhandled line mode %s' % (arg & 0x08))
        self.eight_dots = True
        if arg & 0x04 == 0x04:
            # 5x10DOTS
            self.eight_dots = False
            raise HwException('Unhandled dot height %s' % (arg & 0x04))

    def move(self, mv_right):
        if mv_right:
            return self.move_right()
        return self.move_left()

    def move_right(self):
        for r in self.cells.keys():
            new_r = {}
            for c in range(1, self.cols):
                if (c - 1) in self.cells[r]:
                    new_r[c] = self.cells[r][c - 1]
            self.cells[r] = new_r
        self.out_refresh()

    def move_left(self):
        for r in self.cells.keys():
            if 0 in self.cells[r]:
                del self.cells[r][0]
            for c in range(1, self.cols):
                if c in self.cells[r] and (c - 1) >= 0:
                    self.cells[r][c - 1] = self.cells[r][c]
                    del self.cells[r][c]
        self.out_refresh()

    def displayset(self, arg):
        # NOTE assuming it's turning on a blank screen, hidden cursor
        # Flags for display on/off control
        if arg & 0x04 != 0x04:
            # turn display off
            self.clear()
            return
        if arg & 0x02 == 0x02:
            # TODO show cursor
            raise HwException('Unhandled cursor mode %s' % (arg & 0x02))
        if arg & 0x01 == 0x01:
            # TODO blink, (what, cursor or text?)
            raise HwException('Unhandled blink mode %s' % (arg & 0x02))

    def entryset(self, arg):
        self.entryleft = True
        if arg & 0x02 != 0x02:
            self.entryleft = False
            raise HwException('Unhandled entry direction %s' % (arg & 0x02))
        self.shiftmode_decr = True  # cursor
        if arg & 0x01 == 0x01:
            # display/INCREMENT
            self.shiftmode_decr = False
            raise HwException('Unhandled shift mode %s' % (arg & 0x01))


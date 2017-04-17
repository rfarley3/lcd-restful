# from RPLCD.common import (
#     LCD_MOVERIGHT,
from .codec import hitachi_utf_map
LCD_MOVERIGHT = 0x04


class FakesException(BaseException):
    pass


class HwException(FakesException):
    pass


class GpioException(FakesException):
    pass


class FakeHw(object):
    def __init__(self, rows=4, cols=20, raise_on_unknown=True):
        self.raise_unk = raise_on_unknown
        self.reuse = True  # re-use term output (clear before each print)
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
        self.clear()

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
            # NOTE assuming it's turning on a blank screen, hidden cursor
            # return self.unhandled_cmd(val)  # TODO
            return
        # LCD_ENTRYMODESET
        elif (val >> 2) & 0x01 == 1:
            # set which way text enters, sets autoscroll
            # NOTE assumes ENTRYLEFT
            # return self.unhandled_cmd(val)  # skip, too complicated
            return
        # LCD_RETURNHOME
        elif (val >> 1) & 0x01 == 1:
            return self.set_cursor(0, 0)
        raise HwException('Unexpect command value')

    def unhandled_cmd(self, arg):
        if self.raise_unk:
            raise HwException('Unhandled, but known, cmd %s' % arg)

    def clear(self, *args):
        self.cur_c = 0
        self.cur_r = 0
        self.cells = {}
        for r in range(self.rows):
            self.cells[r] = {}
            # get(, ' ') allows us to skip setting all to ' '
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
            return self.set_cursor(ros[3] - arg, 3)
        elif arg < ros[2]:
            return self.set_cursor(ros[0] - arg, 0)
        elif arg >= ros[1]:
            return self.set_cursor(ros[1] - arg, 1)
        elif arg >= ros[2]:
            return self.set_cursor(ros[2] - arg, 2)
        else:
            raise HwException('Bad cursor pos %s' % arg)

    def funcset(self, val):
        # self.read_width = 4
        if val & 0x10 == 0x10:
            self.read_width = 8
        self.two_line = True  # vs one_line
        if val & 0x08 != 0x08:
            raise HwException('Unhandled line mode %s' % (val & 0x08))
        # LCD_5x10DOTS = 0x04
        # raise HwException('Parsing funcset %s' % val)

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


class FakeGpio(object):
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/common.h
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/c_gpio.h
    MODE_UNKNOWN = -1
    BOARD = 10
    BCM = 11
    OUT = 0
    IN = 1
    LOW = 0
    HIGH = 1

    def __init__(self, hw=None):
        self.hw = hw
        if self.hw is None:
            self.hw = FakeHw()
        self.numbering = self.MODE_UNKNOWN
        self.modes = {}
        self.pins = {}

    def cleanup(self):
        self.modes = {}
        self.pins = {}
        # reset hardware, numbering?

    def setmode(self, mode):
        """Set pin numbering mode"""
        if mode != self.BOARD:
            raise GpioException('Unhandled pin numbering mode %s' % mode)
        self.numbering = mode
        # ?? self.hw._setmode(mode)

    def setup(self, pin, mode):
        """Set mode for each pin (in/out, etc)"""
        # verify possible modes
        self.modes[pin] = mode
        # TODO see if anything else done here
        # assume the pin starts as low (may not be accurate)
        self._set(pin, self.LOW)

    # Called by Adafruit API
    def output_pins(self, pinnums_to_bools):
        """Given a dict of pinnum:val, set multiple pins"""
        for (pin, value) in pinnums_to_bools.items():
            self._set(pin, value)

    # Called by Adafruit and RPLCD API
    def output(self, pin, value):
        """Given a pin number set it to value"""
        self._set(pin, value)

    def _set(self, pin, value):
        """Not in RPi.GPIO, manages Fake state and triggers HW"""
        if pin not in self.modes:
            raise GpioException('Pin %s not setup' % pin)
        if self.modes[pin] != self.OUT:
            raise GpioException('Attempt to IN and OUT pin')
        if value not in [self.LOW, self.HIGH]:
            # TODO handle PWM
            raise GpioException('Unhandled pin value %s' % value)
        self.pins[pin] = value
        self.hw._set(pin, value)


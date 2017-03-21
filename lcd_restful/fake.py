from .lcd import Lcd
from Adafruit_CharLCD import (
    LCD_ROW_OFFSETS,
    LCD_MOVERIGHT,
)


class FakeHw(object):
    def __init__(self, rows=4, cols=20, on_refresh=None):
        self.rs = False
        self.write4_1 = True
        self.cur_c = 0
        self.cur_r = 0
        self.rows = rows
        self.cols = cols
        self.on_refresh = on_refresh
        self.clear()

    def __str__(self):
        lcd_str = ''
        for r in range(self.rows):
            r_str = ''
            for c in range(self.cols):
                r_str += self.cells[r].get(c, ' ')
            lcd_str += r_str + '\n'
        return lcd_str[:-1]

    def write4(self, d4, d5, d6, d7):
        if self.write4_1:
            self.upper = (d7 << 7 | d6 << 6 | d5 << 5 | d4 << 4)
            self.write4_1 = False
            return
        lower = (d7 << 3 | d6 << 2 | d5 << 1 | d4)
        val = self.upper | lower
        self.write4_1 = True
        self.upper = None
        if self.rs:
            self.write8_chr(chr(val))
            return
        self.write8_cmd(val)

    def write8_chr(self, character):
        self.cells[self.cur_r][self.cur_c] = character
        self.cur_c += 1
        if self.on_refresh is not None:
            self.on_refresh(self)

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
            return self.unhandled_cmd(val)  # skip, only seen at init
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
            return self.unhandled_cmd(val)  # TODO
        # LCD_ENTRYMODESET
        elif (val >> 2) & 0x01 == 1:
            # set which way text enters, sets autoscroll
            return self.unhandled_cmd(val)  # skip, too complicated
        # LCD_RETURNHOME
        elif (val >> 1) & 0x01 == 1:
            return self.set_cursor(0, 0)
        raise('Unexpect command value')

    def unhandled_cmd(self, arg):
        raise('Unhandled, but known, cmd %s' % arg)

    def clear(self, *args):
        self.cur_c = 0
        self.cur_r = 0
        self.cells = {}
        for r in range(self.rows):
            self.cells[r] = {}

    def set_cursor(self, col, row):
        self.cur_c = col
        self.cur_r = row

    def cursor(self, arg):
        # LCD_SETDDRAMADDR | (col + LCD_ROW_OFFSETS[row]))
        # LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)
        # (col + LCD_ROW_OFFSETS[row])
        if arg >= LCD_ROW_OFFSETS[3]:
            return self.set_cursor(LCD_ROW_OFFSETS[3] - arg, 3)
        elif arg < LCD_ROW_OFFSETS[2]:
            return self.set_cursor(LCD_ROW_OFFSETS[0] - arg, 0)
        elif arg >= LCD_ROW_OFFSETS[1]:
            return self.set_cursor(LCD_ROW_OFFSETS[1] - arg, 1)
        elif arg >= LCD_ROW_OFFSETS[2]:
            return self.set_cursor(LCD_ROW_OFFSETS[2] - arg, 2)
        else:
            raise('Bad cursor pos')

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
        if self.on_refresh is not None:
            self.on_refresh(self)

    def move_left(self):
        for r in self.cells.keys():
            if 0 in self.cells[r]:
                del self.cells[r][0]
            for c in range(1, self.cols):
                if c in self.cells[r] and (c - 1) >= 0:
                    self.cells[r][c - 1] = self.cells[r][c]
                    del self.cells[r][c]
        if self.on_refresh is not None:
            self.on_refresh(self)


class FakeGpio(object):
    def __init__(self, on_refresh=None):
        self.hw = FakeHw(on_refresh=on_refresh)
        # bc set_pins is called after Lcd.init, rs isn't set
        # when Lcd.init calls self.clear. you can't intercept it.
        self._d4 = None
        self._d5 = None
        self._d6 = None
        self._d7 = None
        self._rs = None
        self._en = None

    def set_pins(self, config):
        self._d4 = config['d4']
        self._d5 = config['d5']
        self._d6 = config['d6']
        self._d7 = config['d7']
        self._rs = config['rs']
        self._en = config['en']

    def setup(self, pin, mode):
        pass

    def output(self, pin, char_mode=False):
        if pin == self._rs:
            self.hw.rs = char_mode

    def output_pins(self, pinnums_to_bools):
        data_pins = set([self._d4, self._d5, self._d6, self._d7])
        if set(pinnums_to_bools.keys()) != data_pins:
            # only time is rgb setting
            return
        # the only time it is called, it is called 2x to make a write8
        self.hw.write4(
            pinnums_to_bools[self._d4],
            pinnums_to_bools[self._d5],
            pinnums_to_bools[self._d6],
            pinnums_to_bools[self._d7])


class FakeLcd(Lcd):
    def __init__(self, config={}):
        self.fake_gpio = FakeGpio(on_refresh=self.on_refresh)
        config.update({'gpio': self.fake_gpio})
        super(FakeLcd, self).__init__(config)
        self._gpio.set_pins(self.config)
        print(self._gpio.hw)

    def _pulse_enable(self):
        pass

    def on_refresh(self, lcd_map=None, self_delete=True):
        if self_delete:
            for r in range(self.config['rows']):
                print('\b' * self.config['cols'], end='')
                print(' ' * self.config['cols'], end='')
                print('\033[A', end='')
            print('\b' * self.config['cols'], end='')
        print(lcd_map)

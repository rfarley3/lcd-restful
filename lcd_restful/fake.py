from .lcd import Lcd
# from Adafruit_CharLCD import (
#     LCD_CLEARDISPLAY,
#     LCD_SETDDRAMADDR
# )


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

    def mv_right(self):
        pass

    def mv_left(self):
        pass

    def write4(self, d4, d5, d6, d7):
        if self.write4_1:
            self.upper = (
                d7 << 7 |
                d6 << 6 |
                d5 << 5 |
                d4 << 4)
            self.write4_1 = False
            return
        lower = (
            d7 << 3 |
            d6 << 2 |
            d5 << 1 |
            d4)
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
        # print('[%s,%s]%s;' % (self.cur_r, self.cur_c, character), end='')

    def unkcmd(self, arg):
        print('unknown cmd %s' % arg)

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
        print('set cursor %s' % arg)

    def write8_cmd(self, val):
        if val & 0x01 == 1:
            # LCD_CLEARDISPLAY
            self.clear()
        elif val >> 7 == 1:
            # LCD_SETDDRAMADDR
            self.cursor(val & 0b01111111)
        elif (val >> 6) & 0x01 == 1:
            # LCD_SETCGRAMADDR
            self.unkcmd(val)
        elif (val >> 5) & 0x01 == 1:
            # LCD_FUNCTIONSET
            self.unkcmd(val)
        elif (val >> 4) & 0x01 == 1:
            # LCD_CURSORSHIFT
            self.unkcmd(val)
        elif (val >> 3) & 0x01 == 1:
            # LCD_DISPLAYCONTROL
            self.unkcmd(val)
        elif (val >> 2) & 0x01 == 1:
            # LCD_ENTRYMODESET
            self.unkcmd(val)
        elif (val >> 1) & 0x01 == 1:
            # LCD_RETURNHOME
            self.unkcmd(val)


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

    # def clear(self):
    #     self._gpio.hw.clear()  # TODO catch at gpio

    def set_cursor(self, col, row):
        self._gpio.hw.set_cursor(col, row)  # TODO catch at gpio
        super(FakeLcd, self).set_cursor(col, row)

    # def message(self, text):
    #     super(FakeLcd, self).message(text)
    #     # self.refresh()

    def move_right(self):
        self._gpio.hw.mv_right()  # TODO catch at gpio
        self.on_refresh()

    def move_left(self):
        self._gpio.hw.mv_left()  # TODO catch at gpio
        self.on_refresh()

    def on_refresh(self, lcd_map=None, self_delete=False):
        if self_delete:
            for r in range(self.config['rows']):
                print('\b' * self.config['cols'], end='')
                print(' ' * self.config['cols'], end='')
                print('\033[A', end='')
            print('\b' * self.config['cols'], end='')
        # TODO remove after remove all self.fake_gpio.hw calls
        if lcd_map is None:
            lcd_map = self._gpio.hw
        print(lcd_map)

    # def write8(self, val, chr_mode=False):
    #     if chr_mode:
    #         print(val)
    #     super(FakeLcd, self).write8(val, chr_mode)

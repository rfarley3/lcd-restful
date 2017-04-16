from RPLCD.common import (
    LCD_MOVERIGHT,
)
# from RPCLD.gpio import CharLCD

from .lcd import Lcd


class FakeHw(object):
    def __init__(self, rows=4, cols=20):
        self.rs = False
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
        print(self)

    def out_refresh(self):
        # TODO allow refreshing single cells, or range of cells
        if self.has_outputted:
            self.out_clear()
        self.out_draw()
        self.has_outputted = True

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
            self.write8_chr(val)
            return
        self.write8_cmd(val)

    def write8_chr(self, char_val):
        mapped_char = self.decode_map.get(char_val)
        self.cells[self.cur_r][self.cur_c] = mapped_char
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
            # get(, ' ') allows us to skip:
            # for c in range(self.cols):
            #     self.cells[r][c] = ' '
        self.out_refresh()

    def set_cursor(self, col, row):
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
    def __init__(self):
        self.hw = FakeHw()
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


class FakeLcdApi(Lcd):
    def __init__(self, config={}):
        self.fake_gpio = FakeGpio()
        config.update({'gpio': self.fake_gpio})
        super(FakeLcdApi, self).__init__(config)
        # pins are set by Lcd.__init__, so have to wait until now to set them within FakeGpio
        self._gpio.set_pins(self.config)

    def _pulse_enable(self):
        pass

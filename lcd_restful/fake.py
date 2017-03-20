from .lcd import Lcd


class FakeHw(object):
    def __init__(self, rows=4, cols=20):
        self.cur_c = 0
        self.cur_r = 0
        self.rows = rows
        self.cols = cols
        self.clear()

    def clear(self):
        self.cur_c = 0
        self.cur_r = 0
        self.cells = {}
        for r in range(self.rows):
            self.cells[r] = {}

    def set_cursor(self, col, row):
        self.cur_c = col
        self.cur_r = row

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

    def write_chr(self, character):
        self.cells[self.cur_r][self.cur_c] = character
        self.cur_c += 1
        # print('[%s,%s]%s;' % (self.cur_r, self.cur_c, character), end='')


class FakeGpio(object):
    def __init__(self):
        self.hw = FakeHw()
        self.in_chr_mode = -1
        self.lower = {}
        self.upper = {}

    def set_pins(self, config):
        self._d4 = config['d4']
        self._d5 = config['d5']
        self._d6 = config['d6']
        self._d7 = config['d7']

    def setup(self, pin, mode):
        pass

    def output_pins(self, vals):
        if self.in_chr_mode == -1:
            return
        elif self.in_chr_mode == 0:
            self.upper = vals
            self.in_chr_mode = 1
            return
        # elif self.in_chr_mode == 1:
        self.lower = vals
        combined = (
            (self.upper[self._d7] << 7) |
            (self.upper[self._d6] << 6) |
            (self.upper[self._d5] << 5) |
            (self.upper[self._d4] << 4) |
            (self.lower[self._d7] << 3) |
            (self.lower[self._d6] << 2) |
            (self.lower[self._d5] << 1) |
             self.lower[self._d4])
        # print('combined: %s' % combined)
        self.hw.write_chr(chr(combined))
        self.in_chr_mode = -1
        self.lower = {}
        self.upper = {}

    def output(self, pin, char_mode):
        if char_mode:
            self.in_chr_mode = 0
            return
        self.in_chr_mode = -1


class FakeLcd(Lcd):
    def __init__(self, config={}):
        self.fake_gpio = FakeGpio()
        config.update({'gpio': self.fake_gpio})
        super(FakeLcd, self).__init__(config)
        self.fake_gpio.set_pins(self.config)
        print(self.fake_gpio.hw)

    def _pulse_enable(self):
        pass

    def clear(self):
        self.fake_gpio.hw.clear()  # TODO catch at gpio

    def set_cursor(self, col, row):
        self.fake_gpio.hw.set_cursor(col, row)  # TODO catch at gpio
        super(FakeLcd, self).set_cursor(col, row)

    def message(self, text):
        super(FakeLcd, self).message(text)
        self.refresh()

    def move_right(self):
        self.fake_gpio.hw.mv_right()  # TODO catch at gpio
        self.refresh()

    def move_left(self):
        self.fake_gpio.hw.mv_left()  # TODO catch at gpio
        self.refresh()

    def refresh(self):
        for r in range(self.config['rows']):
            print('\b' * self.config['cols'], end='')
            print(' ' * self.config['cols'], end='')
            print('\033[A', end='')
        print('\b' * self.config['cols'], end='')
        print(self.fake_gpio.hw)

    # def write8(self, val, chr_mode=False):
    #     if chr_mode:
    #         print(val)
    #     super(FakeLcd, self).write8(val, chr_mode)

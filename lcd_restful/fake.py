from .lcd import Lcd


class FakeHw(object):
    def __init__(self, rows=4, cols=20):
        self.rows = rows
        self.cols = cols
        self.clear()

    def clear(self):
        self.cells = {}
        for r in range(self.rows):
            self.cells[r] = {}

    def __str__(self):
        lcd_str = ''
        for r in range(self.rows):
            r_str = ''
            for c in range(self.cols):
                r_str += self.cells[r].get(c, ' ')
            lcd_str += r_str + '\n'
        return lcd_str[:-1]


class FakeGpio(object):
    def __init__(self):
        pass

    def setup(self, pin, mode):
        pass

    def output_pins(self, *args):
        pass

    def output(self, pin, mode):
        pass


class FakeLcd(Lcd):
    def __init__(self, config={}):
        self.fake_hw = FakeHw()
        config.update({'gpio': FakeGpio()})
        super(FakeLcd, self).__init__(config)

    def clear(self):
        self.cur_c = 0
        self.cur_r = 0
        self.fake_hw.clear()

    def set_cursor(self, col, row):
        self.cur_c = col
        self.cur_r = row
        super(FakeLcd, self).set_cursor(col, row)

    def message(self, text):
        # print('Msg: %s' % text)
        super(FakeLcd, self).message(text)
        print(self.fake_hw)

    def write8(self, value, char_mode=False):
        if char_mode:
            self.fake_hw.cells[self.cur_r][self.cur_c] = chr(value)
            self.cur_c += 1
            # print('[%s,%s]%s(%s);' % (self.cur_r, self.cur_c, chr(value), value), end='')
            # sys.stdout.flush()
            return
        super(FakeLcd, self).write8(value, char_mode)

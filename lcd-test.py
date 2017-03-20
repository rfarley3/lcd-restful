#!/usr/bin/env python3
import sys
import time
import Adafruit_CharLCD as LCD


# Raspberry Pi pin configuration:
lcd_rs        = 25  # LCD Pin 4
lcd_en        = 24  #         6
lcd_d4        = 23  #        11
lcd_d5        = 17  #        12
lcd_d6        = 21  #        13
lcd_d7        = 22  #        14
lcd_backlight = None  #      15

lcd_columns = 20
lcd_rows    = 4


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
                r_str += self.cells[r].get(c, ' '):
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


class FakeLcd(LCD.Adafruit_CharLCD):
    def __init__(self,
            lcd_rs, lcd_en,
            lcd_d4, lcd_d5, lcd_d6, lcd_d7,
            lcd_columns, lcd_rows,
            lcd_backlight):
        self.fake_hw = FakeHw()
        super(FakeLcd, self).__init__(
            lcd_rs, lcd_en,
            lcd_d4, lcd_d5, lcd_d6, lcd_d7,
            lcd_columns, lcd_rows,
            lcd_backlight,
            gpio=FakeGpio(),
            pwm=None)

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
            sys.stdout.flush()
            return
        super(FakeLcd, self).write8(value, char_mode)


def main(argv, lcd):
    lcd.message('Hello\nworld!')
    time.sleep(2.0)

    # Demo showing the cursor.
    lcd.clear()
    lcd.show_cursor(True)
    lcd.message('Show cursor')
    time.sleep(2.0)

    # Demo showing the blinking cursor.
    lcd.clear()
    lcd.blink(True)
    lcd.message('Blink cursor')
    time.sleep(2.0)

    # Stop blinking and showing cursor.
    lcd.show_cursor(False)
    lcd.blink(False)

    # Demo scrolling message right/left.
    lcd.clear()
    message = 'Scroll'
    lcd.message(message)
    for i in range(lcd_columns-len(message)):
        time.sleep(0.5)
        lcd.move_right()
    for i in range(lcd_columns-len(message)):
        time.sleep(0.5)
        lcd.move_left()
    time.sleep(0.5)

    lcd.clear()
    lcd.message('Goodbye!')
    return 0


if __name__ == '__main__':
    # Initialize the LCD using the pins above.
    lcd = FakeLcd(
        lcd_rs, lcd_en,
        lcd_d4, lcd_d5, lcd_d6, lcd_d7,
        lcd_columns, lcd_rows,
        lcd_backlight)
    sys.exit(main(sys.argv, lcd))

#!/usr/bin/env python3
import sys
import time
# from lcd_restful.lcd import Lcd
from lcd_restful.fake import FakeLcdApi as Lcd
from lcd_restful.lcd import HITACHI_CHAR_MAP

# WARNING double check pin configuration in lcd_restful.lcd

def main(argv):
    # print('Char map is %s' % len(HITACHI_CHAR_MAP))
    # for i, ch in enumerate(HITACHI_CHAR_MAP):
    #     print('%s: %s' % (i, ch))
    lcd = Lcd()
    lcd.message('Hello\nworld!')
    time.sleep(1.0)
    lcd.clear()
    lcd.message('1' * 20 + '\n' + '2' * 20 + '\n' + '3' * 20 + '\n' + '4' * 20)
    time.sleep(1.0)
    i = 16
    while i < 256:
        lcd.clear()
        lines = []
        for j in range(4):
            line = ''
            max_i = i + 20
            while i < max_i and i < 256:
                c = chr(i)
                line += c
                i += 1
            lines.append(line)
        msg = '\n'.join(lines)
        lcd.message(msg)
        time.sleep(2.0)

    # # Demo showing the cursor.
    # lcd.clear()
    # lcd.show_cursor(True)
    # lcd.message('Show cursor')
    # time.sleep(2.0)

    # # Demo showing the blinking cursor.
    # lcd.clear()
    # lcd.blink(True)
    # lcd.message('Blink cursor')
    # time.sleep(2.0)

    # # Stop blinking and showing cursor.
    # lcd.show_cursor(False)
    # lcd.blink(False)

    # Demo scrolling message right/left.
    lcd.clear()
    message = 'Scroll'
    lcd.message(message)
    for i in range(lcd._cols - len(message)):
        time.sleep(0.5)
        lcd.move_right()
    for i in range(lcd._cols - len(message)):
        time.sleep(0.5)
        lcd.move_left()
    time.sleep(0.5)

    lcd.clear()
    lcd.message('Goodbye!')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

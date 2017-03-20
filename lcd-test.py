#!/usr/bin/env python3
import sys
import time
# from lcd_restful.lcd import Lcd
from lcd_restful.fake import FakeLcd as Lcd

# WARNING double check pin configuration in lcd_restful.lcd

def main(argv):
    lcd = Lcd()
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
    for i in range(lcd._cols-len(message)):
        time.sleep(0.5)
        lcd.move_right()
    for i in range(lcd._cols-len(message)):
        time.sleep(0.5)
        lcd.move_left()
    time.sleep(0.5)

    lcd.clear()
    lcd.message('Goodbye!')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

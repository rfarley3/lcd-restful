#!/usr/bin/env python
# coding=utf8
import sys
import time
from lcd_restful.lcd import Lcd
from lcd_restful.fake import FakeLcdApi as FakeLcd

# WARNING double check pin configuration in lcd_restful.lcd

def pause(lcd, interact=False):
    if interact:
        input('Press enter for next test')
        print('\033[A', end='')
    else:
        time.sleep(2.0)
    lcd.clear()

def main(argv):
    interact = False
    if '-p' in argv or '--prompt' in argv:
        interact = True
    use_fake = False
    if '-f' in argv or '--fake' in argv:
        use_fake = True
    if not use_fake:
        try:
            lcd = Lcd()
        except FileNotFoundError:  # system detection is via /proc/cpuinfo
            print('Warning, this is not an RPi system, rolling back to fake LCD')
            use_fake = True
    if use_fake:
        lcd = FakeLcd()
    # from lcd_restful.lcd import HITACHI_CHAR_MAP
    # print('Char map is %s' % len(HITACHI_CHAR_MAP))
    # for i, ch in enumerate(HITACHI_CHAR_MAP):
    #     print('%s: %s' % (i, ch))
    lcd.message('Hello\nworld!')
    pause(lcd, interact)
    lcd.message('1' * 20 + '\n' + '2' * 20 + '\n' + '3' * 20 + '\n' + '4' * 20)
    pause(lcd, interact)
    # Show all possible characters on display
    i = 0
    while i < 256:
        lines = []
        for j in range(4):  # lcd.rows
            line = ''
            max_i = i + 20  # lcd.cols
            while i < max_i and i < 256:
                c = i
                line += chr(c)
                i += 1
            lines.append(line)
        lcd.message(lines, as_ordinal=True)
        pause(lcd, interact)
    lcd.message('Testing message that needs autowrap', autowrap=True)
    pause(lcd, interact)
    lcd.message('Testing\nmessage with\ntoo many\nlines\nshould not see me', autowrap=True)
    pause(lcd, interact)
    lcd.message('Testing message by\nutf8 strings')
    pause(lcd, interact)
    test_lines = [
        (' !"#$%&\'()*+,-./\n' +
         '0123456789:;<=>?\n' +
         '@ABCDEFGHIJKLMNO\n' +
         'PQRSTUVWXYZ[¥]^_'),
        ('`abcdefghijklmno\n' +
         'pqrstuvwxyz{|}→←)'),
        (' ｡｢｣､･ｦｧｨｩｪｫｬｭｮｯ\n' +
         'ｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ\n' +
         'ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏ\n' +
         'ﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ゛゜'),
        ('αäβεμσρg√⁻jˣ¢£ñö\n' +
         'pqθ∞ΩüΣπxy千万円÷ █')]
    for l in test_lines:
        lcd.message(l)
        pause(lcd, interact)

    # # Demo showing the cursor.
    # lcd.show_cursor(True)
    # lcd.message('Show cursor')
    # pause(lcd, interact)

    # # Demo showing the blinking cursor.
    # lcd.blink(True)
    # lcd.message('Blink cursor')
    # pause(lcd, interact)

    # # Stop blinking and showing cursor.
    # lcd.show_cursor(False)
    # lcd.blink(False)
    # pause(lcd, interact)

    # Demo scrolling message right/left.
    message = 'Scroll'
    lcd.message(message)
    for i in range(lcd._cols - len(message)):
        time.sleep(0.5)
        lcd.move_right()
    for i in range(lcd._cols - len(message)):
        time.sleep(0.5)
        lcd.move_left()
    pause(lcd, interact)

    lcd.message('Goodbye!')
    pause(lcd, False)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

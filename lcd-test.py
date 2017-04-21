#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import sys
import time
from lcd_restful import Lcd

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
    lcd = Lcd(fake=use_fake)
    lcd.message('Hello\nworld\r\n!!!!!!!!!!')
    pause(lcd, interact)
    lcd.message(
        '1' * 20 + '\r\n' +
        '2' * 20 + '\r\n' +
        '3' * 20 + '\r\n' +
        '4' * 20)
    pause(lcd, interact)
    # Show all possible characters on display
    i = 0
    while i < 256:
        lines = []
        for j in range(4):  # lcd.rows
            line = []
            max_i = i + 20  # lcd.cols
            while i < max_i and i < 256:
                line.append(i)
                i += 1
            lines.append(line)
        lcd.message(lines, as_ordinal=True)
        pause(lcd, interact)
    try:
        lcd.message('Testing a super long message', autowrap=False)
    except IndexError:
        lcd.clear()
        lcd.message('Caught long msg')
    pause(lcd, interact)
    lcd.message('Testing message that needs autowrap', autowrap=True)
    pause(lcd, interact)
    lcd.message(
        'junkkkk\r\n' +
        'Testing\r\n' +
        'message with\r\n' +
        'too many lines\r\n' +
        'rolled 1st line', autowrap=True)
    pause(lcd, interact)
    lcd.message('Testing utf8 to hitachi-code', autowrap=True)
    pause(lcd, interact)
    test_lines = [
        (' !"#$%&\'()*+,-./\r\n' +
         '0123456789:;<=>?\r\n' +
         '@ABCDEFGHIJKLMNO\r\n' +
         'PQRSTUVWXYZ[¥]^_'),
        ('`abcdefghijklmno\r\n' +
         'pqrstuvwxyz{|}→←)'),
        (' ｡｢｣､･ｦｧｨｩｪｫｬｭｮｯ\r\n' +
         'ｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ\r\n' +
         'ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏ\r\n' +
         'ﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ゛゜'),
        ('αäβεμσρg√⁻jˣ¢£ñö\r\n' +
         'pqθ∞ΩüΣπxy千万円÷ █')]
    for l in test_lines:
        lcd.message(l)
        pause(lcd, interact)

    lcd.message('Displaying the particularly odd characters', autowrap=True)
    pause(lcd, interact)
    odd_chars = [
        b'\x67\x6a\x70\x71\x79',
        b'\xe7\xea\xf0\xf1\xf9',
        b'\xe9\xf8',
        b'\xeb\xed\xf6\xff']
    lcd.message(odd_chars, as_ordinal=True)
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
    for i in range(lcd.lcd.cols - len(message)):
        time.sleep(0.5)
        lcd.shift_display(1)
    for i in range(lcd.lcd.cols - len(message)):
        time.sleep(0.5)
        lcd.shift_display(-1)
    pause(lcd, interact)

    lcd.message('Goodbye!')
    pause(lcd, False)
    lcd.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))


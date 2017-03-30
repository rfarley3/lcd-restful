from Adafruit_CharLCD import Adafruit_CharLCD as AdaLcd
from Adafruit_CharLCD import LCD_ENTRYLEFT

from .codec import encode_char


class Lcd(AdaLcd):
    config = {
        'cols': 20,
        'rows': 4,
        'pwm': None,
        'rs': 25,  # LCD Pin 4
        'en': 24,  # -       6
        'd4': 23,  # -      11
        'd5': 17,  # -      12
        'd6': 21,  # -      13
        'd7': 22,  # -      14
    }

    def __init__(self, config={}):
        self.config.update(config)
        super(Lcd, self).__init__(
            self.config['rs'],
            self.config['en'],
            self.config['d4'],
            self.config['d5'],
            self.config['d6'],
            self.config['d7'],
            self.config['cols'],
            self.config['rows'],
            backlight=self.config.get('backlight'),
            gpio=self.config.get('gpio'),
            pwm=self.config.get('pwm'))

    def message(self, text, as_ordinal=False, autowrap=False):
        """Write text to display.  Note that text can include newlines."""
        # as_ordinal write8s each char as an int (ie passes bytes directly through)
        #     it assumes that each line is its own element in a list
        # not as_original treats each char as utf8 and decodes it
        #     it assumes input is a string and splits on newlines
        #     append an empty list in place of a trailing newline (so cursor is at entry)
        if not as_ordinal:
            text = text.split('\n')
        if not isinstance(text, list):
            text = [text]
        if autowrap:
            # TODO consider textwrap package
            text_tmp = []
            for t in text:
                while len(t) > self._cols:
                    text_tmp.append(t[:self._cols])
                    t = t[self._cols:]
                text_tmp.append(t)
            text = text_tmp
        # auto cut off too tall of messages
        text = text[:self._lines]
        # print('writing msg %s' % text)
        for i, line in enumerate(text):
            # Advance to next line if character is a new line.
            if i > 0:
                # Move to left or right side depending on text direction.
                col = 0 if self.displaymode & LCD_ENTRYLEFT > 0 else self._cols-1
                self.set_cursor(col, i)
            # Iterate through each character.
            for char in line:
                # Write the character to the display.
                # print('writing %s' % char)
                if as_ordinal:
                    char = ord(char)
                else:
                    char = encode_char(char)
                self.write8(char, True)

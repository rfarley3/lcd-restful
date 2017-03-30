from Adafruit_CharLCD import Adafruit_CharLCD as AdaLcd
from Adafruit_CharLCD import LCD_ENTRYLEFT

from .codec import hitachi_utf_map, utf_hitachi_map


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
        self.enc_map = utf_hitachi_map()

    def message(self, text, as_ordinal=False):
        """Write text to display.  Note that text can include newlines."""
        if not as_ordinal:
            text = text.split('\n')
        if not isinstance(text, list):
            text = [text]
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
                self.write8(self.encode_char(char, as_ordinal), True)

    def encode_char(self, utf_char, as_ordinal=False):
        if as_ordinal:
            return ord(utf_char)
        # the custom chars are stored as 0-7
        if ord(utf_char) < 8:
            return ord(utf_char)
        if ord(utf_char) < 32:
            return 32
        # assumes no newlines
        hitachi_val = self.enc_map.get(utf_char)
        if hitachi_val is None:
            raise BaseException('invalid input char %s, %s' % (utf_char, ord(utf_char)))
        return hitachi_val

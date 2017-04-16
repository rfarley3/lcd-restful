on_rpi = True
try:
    import RPi.GPIO
except ImportError:
    on_rpi = False
if not on_rpi:
    print('Warning, not in RPi, using mock GPIO')
    import mock
    # Mock RPi.GPIO module (https://m.reddit.com/r/Python/comments/5eddp5/mock_testing_rpigpio/)
    MockRPi = mock.MagicMock()
    modules = {
        'RPi': MockRPi,
        'RPi.GPIO': MockRPi.GPIO,
    }
    patcher = mock.patch.dict('sys.modules', modules)
    patcher.start()
# from .fake import FakeGpio
# import sys
# sys.modules["RPi.GPIO"] = FakeGpio
# import RPLCD
#if imp.lock_held() is True:
#    del sys.modules[moduleName]
#    sys.modules[tmpModuleName] = __import__(tmpModuleName)
#    sys.modules[moduleName] = __import__(tmpModuleName)
# Alignment.left == LCD_ENTRYLEFT
from RPLCD import Alignment
from RPLCD import CharLCD
if not on_rpi:
    from .fake import FakeGpio
    MockRPi.GPIO = FakeGpio


class Lcd(CharLCD):
    config = {
        'cols': 20,
        'rows': 4,
        'rs': 25,  # LCD Pin 4
        'en': 24,  # -       6
        'd4': 23,  # -      11
        'd5': 17,  # -      12
        'd6': 21,  # -      13
        'd7': 22,  # -      14
        'linebreaks': True,
    }

    def __init__(self, config={}, fake=False):
        self.config.update(config)
        super(Lcd, self).__init__(
            pin_rs=self.config['rs'],
            pin_rw=self.config.get('rw'),
            pin_e=self.config['en'],
            pins_data=[
                self.config['d4'],
                self.config['d5'],
                self.config['d6'],
                self.config['d7']],
            pin_backlight=self.config.get('backlight'),
            rows=self.config.get('rows'),
            cols=self.config.get('cols'),
            auto_linebreaks=self.config.get('linebreaks'))
        # pins are set by Lcd.__init__, so have to wait until now to set them within FakeGpio
        if fake:
            self._gpio.set_pins(self.config)

    def message(self, msg, as_ordinal=False, autowrap=False):
        # TODO toggle auto_linebreaks
        if not as_ordinal:
            return self.write_string(msg)
        for line in msg:
            for b in line:
                self.write(b)
            # adjust row number

    def message_1(self, text, as_ordinal=False, autowrap=False):
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
                col = self._cols - 1
                if (self.displaymode & Alignment.left) > 0:
                    col = 0
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


class FakeLcd(Lcd):
    def __init__(self, config={}):
        self.fake_gpio = FakeGpio()
        config.update({'gpio': self.fake_gpio})
        super(FakeLcdApi, self).__init__(config)
        # pins are set by Lcd.__init__, so have to wait until now to set them within FakeGpio
        self._gpio.set_pins(self.config)

    def _pulse_enable(self):
        pass


def patch_fake_gpio():
    print('Warning, not in RPi, using mock GPIO')
    import mock
    # Mock RPi.GPIO module (https://m.reddit.com/r/Python/comments/5eddp5/mock_testing_rpigpio/)
    MockRPi = mock.MagicMock()
    from .fake import FakeGpio
    GPIO = FakeGpio()
    MockRPi.GPIO = GPIO
    modules = {
        'RPi': MockRPi,
        'RPi.GPIO': MockRPi.GPIO,
    }
    patcher = mock.patch.dict('sys.modules', modules)
    patcher.start()

on_rpi = True
# GPIO = None
try:
    import RPi.GPIO
except ImportError:
    on_rpi = False
if not on_rpi:
    patch_fake_gpio()
# else: GPIO = RPi.GPIO
from RPLCD import CharLCD


class Lcd(CharLCD):
    def __init__(self, fake=False):
        if fake and on_rpi:
            patch_fake_gpio()
        super(Lcd, self).__init__(
            rows=4,
            cols=20,
            pin_rs=25,    # 4
            pin_rw=None,  # 5
            pin_e=24,     # 6
            pins_data=[
                23,   # d4 11
                17,   # d5 12
                21,   # d6 13
                22],  # d7 14
            pin_backlight=None,
            auto_linebreaks=False)

    def message(self, msg, as_ordinal=False, autowrap=False):
        # TODO toggle auto_linebreaks
        self.auto_linebreaks = autowrap
        if not as_ordinal:
            return self.write_string(msg)
        for line in msg:
            for b in line:
                self.write(b)
            row, col = self.cursor_pos
            if row < self.lcd.rows - 1:
                self.cursor_pos = (row + 1, 0)


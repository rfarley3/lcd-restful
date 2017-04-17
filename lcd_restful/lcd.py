on_rpi = True
# GPIO = None
try:
    import RPi.GPIO
except ImportError:
    on_rpi = False
if not on_rpi:
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
# else: GPIO = RPi.GPIO
from RPLCD import CharLCD
from RPLCD import Alignment


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
        'linebreaks': True}

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

    def message(self, msg, as_ordinal=False, autowrap=False):
        # TODO toggle auto_linebreaks
        if not as_ordinal:
            return self.write_string(msg)
        for line in msg:
            for b in line:
                self.write(b)
            # TODO adjust row number


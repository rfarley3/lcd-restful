from .fake import Hw as FakeHw, FakesException


class GpioException(FakesException):
    pass


class Gpio(object):
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/common.h
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/c_gpio.h
    MODE_UNKNOWN = -1
    BOARD = 10
    BCM = 11
    OUT = 0
    IN = 1
    LOW = 0
    HIGH = 1

    def __init__(self, hw=None, **kwargs):
        self.hw = hw
        if self.hw is None:
            self.hw = FakeHw(**kwargs)
        self.numbering = self.MODE_UNKNOWN
        self.modes = {}
        self.pins = {}

    def cleanup(self):
        self.modes = {}
        self.pins = {}
        # reset hardware, numbering?

    def setmode(self, mode):
        """Set pin numbering mode"""
        if mode != self.BOARD:
            raise GpioException('Unhandled pin numbering mode %s' % mode)
        self.numbering = mode
        # ?? self.hw._setmode(mode)

    def setup(self, pin, mode):
        """Set mode for each pin (in/out, etc)"""
        # verify possible modes
        self.modes[pin] = mode
        # TODO see if anything else done here
        # assume the pin starts as low (may not be accurate)
        self._set(pin, self.LOW)

    # Called by Adafruit API
    def output_pins(self, pinnums_to_bools):
        """Given a dict of pinnum:val, set multiple pins"""
        for (pin, value) in pinnums_to_bools.items():
            self._set(pin, value)

    # Called by Adafruit and RPLCD API
    def output(self, pin, value):
        """Given a pin number set it to value"""
        self._set(pin, value)

    def _set(self, pin, value):
        """Not in RPi.GPIO, manages Fake state and triggers HW"""
        if pin not in self.modes:
            raise GpioException('Pin %s not setup' % pin)
        if self.modes[pin] != self.OUT:
            raise GpioException('Attempt to IN and OUT pin')
        if value not in [self.LOW, self.HIGH]:
            # TODO handle PWM
            raise GpioException('Unhandled pin value %s' % value)
        self.pins[pin] = value
        self.hw._set(pin, value)


class GpioException(BaseException):
    pass


class Gpio(object):
    IS_A_FAKE = True  # canary for has_attr
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/common.h
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/c_gpio.h
    MODE_UNKNOWN = -1
    BOARD = 10
    BCM = 11
    OUT = 0
    IN = 1
    LOW = 0
    HIGH = 1

    def __init__(self):  #, hw=None, **kwargs):
        # start of with None to avoid .fake's import before patching done
        self.hw = None
        self.numbering = self.MODE_UNKNOWN
        self.modes = {}
        self.pins = {}

    def cleanup(self, pin=None):
        # resets any setup'ed pins to input with no pud
        if pin is not None:
            del self.modes[pin]
            del self.pins[pin]
        self.modes = {}
        self.pins = {}
        # reset hardware, numbering?

    def setmode(self, mode):
        """Set pin numbering mode"""
        self.numbering = mode
        # ?? self.hw._setmode(mode)

    def setup(self, pin, mode, initial=None, pull_up_down=None):
        """Set mode for each pin (in/out, etc)"""
        # TODO verify possible modes
        self.modes[pin] = mode
        # TODO look at RPi.GPIO to see if anything else done here
        # assume the pin starts as low (may not be accurate)
        if initial is None:
            initial = self.LOW
        self._set(pin, initial)

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


###############################
# Other unimplemented functions

# carp if any pin you set has different mode (or anything other than input)
# could be bad cleanup, or multiple simultaneous GPIO instances
# def setwarnings(mode):

# return function/mode of pin, can be:
# INPUT, OUTPUT, SPI, I2C, HARD_PWM, SERIAL, UNKNOWN
# def gpio_function(pin):

# read value of pin (opposite of output)
# def input(pin):

# create a PWM obj for pin
# def PWM(pin, frequency):


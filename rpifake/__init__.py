from __future__ import print_function
import sys


from .gpio import Gpio


is_active = False
FakeGpio = Gpio()


# After this function, any futher calls to import RPi.GPIO
# will instead import .gpio.Gpio instead
def patch_fake_gpio():
    import sys
    import mock
    global is_active
    print('Overriding RPi.GPIO with fake GPIO', file=sys.stderr)
    # Idea taken from RPLCD who commented it as being from:
    # reddit.com/r/Python/comments/5eddp5/mock_testing_rpigpio
    MockRPi = mock.MagicMock()
    MockRPi.GPIO = FakeGpio
    modules = {
        'RPi': MockRPi,
        'RPi.GPIO': MockRPi.GPIO,
    }
    # handles future imports
    sys.modules.update(modules)
    # previous imports of RPLCD create a GPIO obj
    # within scope of RPLCD.gpio, this overrides them
    sys.modules['RPLCD.gpio'].GPIO = FakeGpio
    is_active = True


# Test if we have RPi.GPIO or not
rpi_gpio_exists = True
if sys.version_info < (3,):
    import imp
    try:
        imp.find_module('RPi')
    except ImportError:
        rpi_gpio_exists = False
else:
    import importlib.util
    if importlib.util.find_spec('RPi') is None:
        rpi_gpio_exists = False
if not rpi_gpio_exists:
    patch_fake_gpio()
# now that the patching is done, we can import RPLCD anywhere

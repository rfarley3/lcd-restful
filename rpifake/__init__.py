from __future__ import print_function
# After this function, any futher calls to import RPi.GPIO
# will instead import .gpio.Gpio instead
is_active = False

def patch_fake_gpio():
    import sys
    import mock
    from .gpio import Gpio as FakeGpio
    global is_active
    print('Warning, not in RPi, using mock GPIO', file=sys.stderr)
    # Idea taken from RPLCD who commented it as being from:
    # reddit.com/r/Python/comments/5eddp5/mock_testing_rpigpio
    MockRPi = mock.MagicMock()
    MockRPi.GPIO = FakeGpio()
    modules = {
        'RPi': MockRPi,
        'RPi.GPIO': MockRPi.GPIO,
    }
    sys.modules.update(modules)
    is_active = True


# Test if we have RPi.GPIO or not
import sys
rpi_gpio_exists = False
if sys.version_info < (3,):
    import imp
    try:
        imp.find_module('RPi')
    except ImportError:
        rpi_gpio_exists = False
else:
    import importlib.util
    if importlib.util.find_spec('RPi') is not None:
        rpi_gpio_exists = False
if not rpi_gpio_exists:
    patch_fake_gpio()
# now that the patching is done, we can import RPLCD anywhere


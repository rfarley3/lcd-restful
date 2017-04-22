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


# Do the test if we have RPi.GPIO or not
try:
    import RPi.GPIO
except ImportError:
    patch_fake_gpio()
# now that the patching is done, we can import RPLCD anywhere


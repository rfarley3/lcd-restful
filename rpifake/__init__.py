# After this function, any futher calls to import RPi.GPIO
# will instead import .gpio.Gpio instead
def patch_fake_gpio():
    print('Warning, not in RPi, using mock GPIO')
    # Idea taken from RPLCD who commented it as being from:
    # reddit.com/r/Python/comments/5eddp5/mock_testing_rpigpio
    import mock
    from .gpio import Gpio as FakeGpio
    MockRPi = mock.MagicMock()
    MockRPi.GPIO = FakeGpio()
    modules = {
        'RPi': MockRPi,
        'RPi.GPIO': MockRPi.GPIO,
    }
    patcher = mock.patch.dict('sys.modules', modules)
    patcher.start()


# Do the test if we have RPi.GPIO or not
ON_RPI = True
try:
    import RPi.GPIO
except ImportError:
    ON_RPI = False
if not ON_RPI:
    patch_fake_gpio()
# now that the patching is done, we can import RPLCD anywhere


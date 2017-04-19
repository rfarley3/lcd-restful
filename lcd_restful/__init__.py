DEBUG = True
BOTTLE_DEBUG = False
PORT = 1234  # as numbers of letters of the alphabet for LCD
COMPACT = True  # re-use same 4x20 characters in the term (when in fake mode)


# After this function, any futher calls to import RPi.GPIO actually
# import .gpio.Gpio instead
def patch_fake_gpio():
    print('Warning, not in RPi, using mock GPIO')
    # Idea taken from RPLCD who commented it as being from:
    # reddit.com/r/Python/comments/5eddp5/mock_testing_rpigpio
    import mock
    from .gpio import Gpio as FakeGpio
    MockRPi = mock.MagicMock()
    MockRPi.GPIO = FakeGpio()  # hw=FakeHw(compact=True))
    modules = {
        'RPi': MockRPi,
        'RPi.GPIO': MockRPi.GPIO,
    }
    patcher = mock.patch.dict('sys.modules', modules)
    patcher.start()


# .fake imports RPLCD.common, and RPCLD.__init__ imports RPi.GPIO
# So we can't import .fake until RPi is taken care of
def inject_hw():
    import sys
    from .fake import Hw as FakeHw
    sys.modules['RPi.GPIO'].hw = FakeHw(compact=COMPACT)


# Do the test if we have RPi.GPIO or not
ON_RPI = True
try:
    import RPi.GPIO
except ImportError:
    ON_RPI = False
if not ON_RPI:
    patch_fake_gpio()
    inject_hw()
# now that the patching is done, we can import RPLCD anywhere


from .lcd import Lcd  # noqa
from .api import Client  # noqa


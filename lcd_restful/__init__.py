import rpifake


DEBUG = True
BOTTLE_DEBUG = False
PORT = 1234  # as numbers of letters of the alphabet for LCD
COMPACT = True  # re-use same 4x20 characters in the term (when in fake mode)


# .fake imports RPLCD.common, and RPCLD.__init__ imports RPi.GPIO
# So we can't import .fake until RPi is taken care of by rpifake.__init__
def inject_fake_hw():
    import sys
    from .fake import Hw as FakeHw
    sys.modules['RPi.GPIO'].hw = FakeHw(compact=COMPACT)


def override_rpigpio():
    if not rpifake.is_active:
        rpifake.patch_fake_gpio()
    inject_fake_hw()


if rpifake.is_active:
    inject_fake_hw()

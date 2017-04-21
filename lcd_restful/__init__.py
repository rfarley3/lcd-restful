DEBUG = True
BOTTLE_DEBUG = False
PORT = 1234  # as numbers of letters of the alphabet for LCD
COMPACT = True  # re-use same 4x20 characters in the term (when in fake mode)

try:
    import RPi.GPIO
except:
    import rpifake
# .fake imports RPLCD.common, and RPCLD.__init__ imports RPi.GPIO
# So we can't import .fake until RPi is taken care of
import sys
if 'RPi.GPIO' in sys.modules and hasattr(sys.modules['RPi.GPIO'], 'IS_A_FAKE'):
    from .fake import Hw as FakeHw
    sys.modules['RPi.GPIO'].hw = FakeHw(compact=COMPACT)

from .lcd import Lcd  # noqa
from .api import Client  # noqa


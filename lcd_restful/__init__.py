DEBUG = True
BOTTLE_DEBUG = False
PORT = 1234  # as numbers of letters of the alphabet for LCD

from .lcd import Lcd, FakeLcd  # noqa
from .api import Client  # noqa


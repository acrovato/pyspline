__version__ = "1.5.1"

# On windows, external shared libraries must be added explicitly
import platform, os, sys
if 'Windows' in platform.uname() and sys.version_info.minor >= 8:
    for v in os.environ['path'].split(';'):
        if 'intel' in v.lower() and 'compiler' in v.lower() and 'redist' in v.lower():
            os.add_dll_directory(v)
            break

from .pyCurve import Curve
from .pySurface import Surface
from .pyVolume import Volume

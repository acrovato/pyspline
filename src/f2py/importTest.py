#! /usr/bin/env python
# Standard Python modules
import sys

print("Testing if module pyspline can be imported...")
try:
    # On windows, external shared libraries must be added explicitly
    import platform, os
    if 'Windows' in platform.uname() and sys.version_info.minor >= 8:
        for v in os.environ['path'].split(';'):
            if 'intel' in v.lower() and 'compiler' in v.lower() and 'redist' in v.lower():
                print('Adding DLL directory:', v)
                os.add_dll_directory(v)
                break
    # External modules
    import libspline  # noqa: F401
except ImportError:
    print("Error importing libspline.so")
    sys.exit(1)
# end try

print("Module libspline was successfully imported.")

"""
This module contains global variables used throughout the application. It is
used to store variables which are used by multiple modules, such as the
application window and the settings file.
"""

# Contains the pointer to the root application window
app = None

# A configparser object which contains the settings from the settings file
settings = None

# A dict holding additional context information for commentary
context = None

# The IRSDK object
ir = None
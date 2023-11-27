"""
This module contains global variables used throughout the application. It also
contains a function to check if iRacing is running.
"""

def check_iracing():
    """Check if iRacing is running.

    Returns:
        bool: True if iRacing is running, False otherwise.
    """
    # Get iRacing connection status
    initialized = ir.is_initialized
    connected = ir.is_connected

    # If iRacing is not running, shut down the SDK and return False
    if not (initialized and connected):
        ir.shutdown()
        return False
    
    # If iRacing is running, return True
    elif ir.startup() and initialized and connected:
        return True

# Contains the pointer to the root application window
app = None

# A configparser object which contains the settings from the settings file
settings = None

# A dict holding additional context information for commentary
context = None

# The IRSDK object
ir = None
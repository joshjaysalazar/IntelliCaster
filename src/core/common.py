"""
This module contains global variables used throughout the application. It also
contains a function to check if iRacing is running.
"""

def check_iracing():
    """Check if iRacing is running.

    Checks if iRacing is running by checking the connection status of the
    IRSDK object. If iRacing is not running, the IRSDK object is shut down.
    If iRacing is running, the IRSDK object is started up and the connection
    is established.

    Returns:
        bool: True if iRacing is running, False otherwise.
    """
    # Try to start up the IRSDK object
    try:
        ir.startup()

        # If the IRSDK object is initialized and connected, return True
        if ir.is_initialized and ir.is_connected:
            return True
        
        # Otherwise, shut down the IRSDK object and return False
        else:
            ir.shutdown()
            return False

    # If the IRSDK object cannot be started, return False
    except:
        ir.shutdown()
        return False

# Contains the pointer to the root application window
app = None

# A configparser object which contains the settings from the settings file
settings = None

# A dict holding additional context information for commentary
context = None

# The IRSDK object
ir = None
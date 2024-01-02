"""
This module contains global variables used throughout the application. It also
contains functions that are used by multiple modules.
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
    
def remove_numbers(name):
    """Remove digits from a driver's name string.

    This method takes a name string that may contain digits and removes
    those digits.

    Args:
        name (str): The driver's name possibly containing digits.

    Returns:
        str: The driver's name without any digits.
    """
    # Create a list of digits
    digits = [str(i) for i in range(10)]

    # Remove any digits from the name
    for digit in digits:
        name = name.replace(digit, "")
    
    # Return the name
    return name

# Contains the pointer to the root application window
app = None

# A configparser object which contains the settings from the settings file
settings = None

# A dict holding additional context information for commentary
context = None

# The IRSDK object
ir = None

# Dictionaries to track the status of the drivers
drivers = []
prev_drivers = []

# Race status variables
race_started = False
start_time = None
race_time = 0
all_cars_started = False

# Recording start time
recording_start_time = None

# Flag to track whether or not commentary is running
running = False

# Additional instructions to give to commentary generation depending on event
instructions = {
    "stopped": "Don't assume the reason for the stoppage.",
    "overtake": "Be sure to include the position of the driver."
}
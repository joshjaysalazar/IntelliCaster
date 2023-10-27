import irsdk
from pprint import pprint

ir = irsdk.IRSDK()
ir.startup()

# Get the drivers
drivers = ir['DriverInfo']['Drivers']
pprint(drivers)
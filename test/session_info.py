import irsdk
from pprint import pprint

ir = irsdk.IRSDK()
ir.startup()

# Get the driver info
driver_info = ir["DriverInfo"]
pprint(driver_info["Drivers"])

for session in ir["SessionInfo"]["Sessions"]:
    if session["SessionName"] == "QUALIFY":
        quali = session["ResultsPositions"]

# pprint(quali)
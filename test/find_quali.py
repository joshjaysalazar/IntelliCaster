import irsdk
from pprint import pprint

ir = irsdk.IRSDK()
ir.startup()

# Get the session info
session_info = ir["SessionInfo"]

pprint(session_info["Sessions"])

quali_list = []
for session in ir["SessionInfo"]["Sessions"]:
    if session["SessionName"] == "QUALIFY":
        for car in session["ResultsPositions"]:
            quali_list.append(car["CarIdx"])

# print(quali_list)
# pprint(ir["DriverInfo"]["Drivers"])
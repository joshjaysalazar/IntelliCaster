import irsdk
from pprint import pprint

ir = irsdk.IRSDK()
ir.startup()

last_laps = ir["CarIdxLapDistPct"]

print(last_laps)
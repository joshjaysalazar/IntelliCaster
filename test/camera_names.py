import irsdk
from pprint import pprint


ir = irsdk.IRSDK()
ir.startup()

pprint(ir["CameraInfo"])
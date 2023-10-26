import irsdk
from pprint import pprint


ir = irsdk.IRSDK()
ir.startup()

# pprint(ir["CameraInfo"])

cameras = {}
for camera in ir["CameraInfo"]["Groups"]:
    cameras[camera["GroupName"]] = camera["GroupNum"]

pprint(cameras)
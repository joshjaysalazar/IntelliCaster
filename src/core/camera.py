class Camera:
    def __init__(self, ir):
        # Member variables
        self.ir = ir

        # Camera Dictionary
        self.cameras = self.get_cameras()

    def get_cameras(self):
        # Create an empty dictionary
        cameras = {}

        # Populate the dictionary with the camera names and numbers
        for camera in self.ir["CameraInfo"]["Groups"]:
            cameras[camera["GroupName"]] = camera["GroupNum"]

        # Return the dictionary
        return cameras
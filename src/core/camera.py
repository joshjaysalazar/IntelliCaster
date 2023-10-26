class Camera:
    """Class for changing cameras in iRacing

    Attributes:
        ir (irsdk.IRSDK): Instance of the IRSDK class
        cameras (dict): Dictionary of camera names and numbers
    """
    
    def __init__(self, ir):
        """Initializes the Camera class
        
        Args:
            ir (irsdk.IRSDK): Instance of the IRSDK class
        """
        # Member variables
        self.ir = ir

        # Camera Dictionary
        self.cameras = self.get_cameras()

    def change_camera(self, car_idx, camera_name):
        """Changes the camera for a specific car
        
        Args:
            car_idx (int): Index of the car
            camera_name (str): Name of the camera
        """
        self.ir.cam_switch_num(car_idx, self.cameras[camera_name])

    def get_cameras(self):
        """Returns a dictionary of camera names and numbers
        
        Returns:
            dict: Dictionary of camera names and numbers
        """
        # Create an empty dictionary
        cameras = {}

        # Populate the dictionary with the camera names and numbers
        for camera in self.ir["CameraInfo"]["Groups"]:
            cameras[camera["GroupName"]] = camera["GroupNum"]

        # Return the dictionary
        return cameras
import random

from core import common


class Camera:
    """Class for changing cameras in iRacing"""
    
    def __init__(self):
        """Initializes the Camera class

        Attributes:
            cameras (dict): Dictionary of camera names and numbers
        """

        # Camera Dictionary
        self.cameras = self._get_cameras()

    def _get_cameras(self):
        """Returns a dictionary of camera names and numbers
        
        Returns:
            dict: Dictionary of camera names and numbers
        """
        # Create an empty dictionary
        cameras = {}

        # Populate the dictionary with the camera names and numbers
        for camera in common.ir["CameraInfo"]["Groups"]:
            cameras[camera["GroupName"]] = camera["GroupNum"]

        # If realistic cameras is enabled, remove unrealistic cameras
        if common.settings["commentary"]["realistic_camera"] == "1":
            cams_to_remove = (
                "LF Susp",
                "RF Susp",
                "LR Susp",
                "RR Susp",
                "Cockpit",
                "Chase",
                "Far Chase",
                "Rear Chase"
            )
            for cam in cams_to_remove:
                del cameras[cam]
                
        # Return the dictionary
        return cameras
    
    def change_camera(self, car_idx, camera_name):
        """Changes the camera for a specific car
        
        Args:
            car_idx (int): Index of the car
            camera_name (str): Name of the camera
        """
        common.ir.cam_switch_num(car_idx, self.cameras[camera_name])

    def choose_random_camera(self, car_idx):
        """Chooses a random camera for a specific car
        
        Args:
            car_idx (int): Index of the car
        """
        # Choose a random camera
        random_camera = random.choice(list(self.cameras.keys()))

        # Change the camera
        self.change_camera(car_idx, self.cameras[random_camera])
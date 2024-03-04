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
                if cam in cameras:
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
        # Get the cameras
        cameras = list(self.cameras.keys())

        # Remove angles that don't focus on a specific car
        bad_angles = ("Scenic", "Pit Lane", "Pit Lane 2")
        for angle in bad_angles:
            if angle in cameras:
                cameras.remove(angle)

        # Set the probability of the cameras
        weights = []
        for camera in cameras:
            if "TV" in camera:
                weights.append(10)
            else:
                weights.append(1)

        # Choose a random camera
        random_camera = random.choices(cameras, weights=weights, k=1)[0]

        # Change the camera
        self.change_camera(car_idx, random_camera)
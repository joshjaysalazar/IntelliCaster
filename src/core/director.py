import os
import random
import threading
import time

from core import camera
from core import common
from core import commentary
from core import events


class Director:
    """
    Manages the overall direction of race broadcast.
    
    The Director class orchestrates the broadcast by monitoring the state of 
    the race and generating commentary. It interfaces with the iRacing SDK to 
    collect real-time data, maintains the state of drivers, detects events, and
    coordinates with the generator classes to generate commentary.
    """

    def __init__(self):
        """Initialize the Director class with necessary settings and utilities.

        Attributes:
            race_started (bool): Flag to indicate if the race has started.
            race_start_time (float): Stores the time the race starts.
            race_time (float): Stores the elapsed time since the race started.
            all_cars_started (bool): Flag to indicate if all cars have started.
            recording_start_time (float): Stores the time recording starts.
            events (Events): The events manager.
            commentary (Commentary): The commentary generator.
            camera (Camera): The camera manager.
        """

        # Track race start status
        self.race_started = False
        self.race_start_time = None
        self.race_time = 0
        self.all_cars_started = False

        # Track recording start time
        self.recording_start_time = None

        # Create the events manager
        self.events = events.Events()

        # Create the commentary generator
        self.commentary = commentary.Commentary()

        # Create a variable for the camera manager (initialized when run)
        self.camera = None

        # Set running to False
        common.running = False

    def check_all_cars_started(self):
        """Check if all cars in the race have started.

        This method checks if all cars have crossed the starting line and 
        started racing. It considers the race time, drivers' laps completed, and
        lap percentages.

        Returns:
            bool: True if all cars have started, False otherwise.
        """
        # If drivers list is empty, return False
        if common.drivers == []:
            return False

        # Check if race recently started
        if self.race_time <= 20:
            # Check if each car has crossed the line
            for driver in common.drivers:           
                d = driver["laps_completed"] + driver["lap_percent"]
                # If between 0.8 and 1, car hasn't started first lap
                if 0.8 < d < 1:
                    return False
                
                # If 0, car hasn't started
                elif d == 0:
                    return False

        # If all cars have started, return True
        return True

    def create_drivers(self):
        """Create a list of drivers.

        This method creates a list of drivers from the iRacing SDK. It is called
        when the Director class is initialized.

        Returns:
            list: A list of dictionaries containing driver data.
        """
        # Create an empty list to track drivers
        driver_dict = []

        # Get driver data from iRacing SDK
        driver_data = common.ir["DriverInfo"]["Drivers"]

        # Get quali results
        for session in common.ir["SessionInfo"]["Sessions"]:
            if session["SessionName"] == "QUALIFY":
                quali = session["ResultsPositions"]

        # Create a dictionary for each driver
        for driver in driver_data:
            # Skip the pace car
            if driver["CarIdx"] == 0:
                continue

            # Get the driver's quali position
            for car in quali:
                if car["CarIdx"] == driver["CarIdx"]:
                    quali_pos = car["Position"]

            # Add the driver to the list
            driver_dict.append(
                {
                    "car_name": driver["CarScreenNameShort"],
                    "fastest_lap": None,
                    "gap_to_leader": None,
                    "grid_position": quali_pos,
                    "idx": driver["CarIdx"],
                    "in_pits": False,
                    "incidents": driver["CurDriverIncidentCount"],
                    "irating": driver["IRating"],
                    "lap_percent": 0,
                    "laps_completed": 0,
                    "laps_started": 0,
                    "last_lap": None,
                    "license": driver["LicString"],
                    "name": driver["UserName"],
                    "number": driver["CarNumberRaw"],
                    "on_track": False,
                    "position": quali_pos
                }
            )

        # Sort the list by grid position
        driver_dict.sort(key=lambda x: x["grid_position"])

        # Return the list of drivers
        return driver_dict

    # def detect_overtakes(self, prev_drivers):
    #     """Detect and report overtakes during the race.

    #     This method iterates through the current list of drivers and compares
    #     their positions with their positions from a previous snapshot
    #     (prev_drivers). If a driver has moved up in position, an overtake is
    #     detected and appropriate commentary is generated. The camera will also
    #     focus on the overtaking driver.

    #     Args:
    #         prev_drivers (list): A list of dictionaries containing the previous
    #             state of each driver.
                
    #     Note:
    #         Overtakes are not reported under specific conditions, like if a
    #         driver is in the pits, has a DNF status, or if the overtaken driver
    #         is not found in the current list.
    #     """
    #     # Go through all the drivers
    #     for driver in common.drivers:
    #         # Get this driver's previous information
    #         prev_driver = None
    #         for item in prev_drivers:
    #             if item["name"] == driver["name"]:
    #                 prev_driver = item
    #                 break

    #         # If a driver's position has decreased, they have overtaken someone
    #         if prev_driver and driver["position"] < prev_driver["position"]:
    #             # Find the driver whose position is 1 higher than this driver's
    #             overtaken = None
    #             for item in common.drivers:
    #                 if item["position"] == driver["position"] + 1:
    #                     overtaken = item
    #                     break
                
    #             # If no driver was found, don't report overtake
    #             if not overtaken:
    #                 continue

    #             # If either driver is in the pits, don't report overtake
    #             if driver["in_pits"] or overtaken["in_pits"]:
    #                 continue

    #             # If laps completed is negative (DNF), don't report overtake
    #             if driver["laps_completed"] < 0:
    #                 continue
    #             if overtaken["laps_completed"] < 0:
    #                 continue

    #             # If an legitimate overtake was found, generate the commentary
    #             driver_name = self.remove_numbers(driver["name"])
    #             overtaken_name = self.remove_numbers(overtaken["name"])
    #             output = (
    #                 f"{driver_name} has overtaken "
    #                 f"{overtaken_name} for "
    #                 f"P{driver['position']}"
    #             )
        
    #             # Move the camera to focus on the overtaking driver
    #             self.camera.change_camera(driver["number"], "TV1")

    #             # Generate the commentary
    #             self.commentary.generate(
    #                 output,
    #                 "play-by-play",
    #                 "neutral",
    #                 "Be sure to include the position of the overtaking driver.",
    #                 yelling=True,
    #                 rec_start_time=self.recording_start_time
    #             )

    #             # Occassionally, generate color commentary
    #             chance = float(common.settings["commentary"]["color_chance"])
    #             if random.random() < chance:
    #                 self.commentary.generate(
    #                     "Add color commentary to the previous overtake.",
    #                     "color",
    #                     "neutral",
    #                     yelling=True,
    #                     rec_start_time=self.recording_start_time
    #                 )

    #             # End this iteration of the loop
    #             break

    def report_event(self, event):
        """Report an event.

        This method reports an event by generating commentary and changing the
        camera focus.

        Args:
            event (dict): A dictionary containing information about the event.
        """
        # Move the camera to focus on the event
        self.camera.change_camera(event["focus"], "TV1")

        # Get how long ago the event happened
        time_since_event = time.time() - event["timestamp"]

        # Generate the commentary
        self.commentary.generate(
            event["description"] + f" {time_since_event} seconds ago.",
            "play-by-play",
            "neutral",
            "Be sure to include the position of the driver.",
            yelling=True,
            rec_start_time=self.recording_start_time
        )

        # Occassionally, generate color commentary
        chance = float(common.settings["commentary"]["color_chance"])
        if random.random() < chance:
            self.commentary.generate(
                "Add color commentary to the previous commentary.",
                "color",
                "neutral",
                yelling=True,
                rec_start_time=self.recording_start_time
            )

    def run(self):
        """The main loop for the Director class.

        This method keeps running as long as the director is set to run. It
        handles all of the logic for generating commentary.
        """
        # Create the drivers dict
        common.drivers = self.create_drivers()

        # Create the camera manager
        self.camera = camera.Camera()

        # Keep running until told to stop
        while common.running:
            # Detect if the race has started
            if common.ir["RaceLaps"] > 0 and not self.race_started:
                self.race_started = True
                self.race_start_time = common.ir["SessionTime"]

            # If the race has already started, update the race length
            elif self.race_started:
                self.race_time = common.ir["SessionTime"] - self.race_start_time

            # If the race hasn't started yet, focus on the front of the grid
            if not self.race_started:
                # Get all the current track positions
                positions = common.ir["CarIdxLapDistPct"]

                # Get the quali results
                for session in common.ir["SessionInfo"]["Sessions"]:
                    if session["SessionName"] == "QUALIFY":
                        quali = session["ResultsPositions"]
                
                # Get driver numbers and add them to quali results
                for driver in common.ir["DriverInfo"]["Drivers"]:
                    for car in quali:
                        if car["CarIdx"] == driver["CarIdx"]:
                            car["Number"] = int(driver["CarNumber"])

                focus = 999
                driver = 0
                for i, pos in enumerate(positions):
                    # Skip the first position (pace car)
                    if i == 0:
                        continue
                    # If car is in pits, skip
                    if common.ir["CarIdxOnPitRoad"][i] == True:
                        continue
                    # If position is less than 0 (haven't gridded yet), skip
                    if pos < 0:
                        continue
                    # Find the gridded car with the best qualifying position
                    for car in quali:
                        if car["CarIdx"] == i:
                            if car["Position"] < focus:
                                focus = car["Position"]
                                driver = car["Number"]

                # Switch to the first car that's not in the pits
                self.camera.change_camera(driver, "TV1")

            # Check if all cars have crossed the start line if needed
            if not self.all_cars_started:
                self.all_cars_started = self.check_all_cars_started()

            # If the race has started, generate commentary
            if self.race_started and self.all_cars_started:
                # Get the next event to generate commentary for
                event = self.events.get_next_event()

                # If an event was found, report it
                if event:
                    self.report_event(event)
            
            # Wait the amount of time specified in the settings
            time.sleep(float(common.settings["director"]["update_frequency"]))

    def start(self):
        """Start the director.

        This method starts the director by updating iRacing settings, jumping
        to the beginning of the current session, hiding the UI, starting the
        replay, and starting iRacing video capture. It then sets the running
        flag to True and starts the director thread.
        """
        # Update iRacing settings
        self.update_iracing_settings()

        # Jump to beginning of current session, wait for iRacing to catch up
        common.ir.replay_search(2)
        time.sleep(1)

        # Hide UI
        common.ir.cam_set_state(8)

        # Start replay
        common.ir.replay_set_play_speed(1)

        # Start iRacing video capture
        common.ir.video_capture(1)

        # Set recording start time
        self.recording_start_time = time.time()

        # Wait for iRacing to catch up
        time.sleep(1)

        # Set running to True
        common.running = True

        # Start the events thread
        threading.Thread(target=self.events.run).start()

        # Start the director thread
        threading.Thread(target=self.run).start()

    def stop(self):
        """Stop the director.

        This method stops the director by setting the running flag to False,
        stopping iRacing video capture, and stopping the replay.
        """
        # Set running to False
        common.running = False

        # Stop iRacing video capture
        common.ir.video_capture(2)

        # Stop replay
        common.ir.replay_set_play_speed(0)

        # Shut down the IRSDK object
        common.ir.shutdown()
            
    def update_iracing_settings(self):
        """Update iRacing settings to enable video capture.

        This method updates the iRacing app.ini file to enable video capture
        and set the video format, framerate, and resolution.
        """
        # Get the iRacing directory
        path = common.settings["general"]["iracing_path"]

        # Read app.ini
        with open(os.path.join(path, "app.ini"), "r") as f:
            app_ini = f.read()

        # Enable video capture if it's not already enabled
        app_ini = app_ini.replace("vidCaptureEnable=0", "vidCaptureEnable=1")

        # Disable microphone capture if it's not already disabled
        app_ini = app_ini.replace("videoCaptureMic=1", "videoCaptureMic=0")

        # Set the video file format
        if common.settings["general"]["video_format"] == "mp4":
            format = 0
        elif common.settings["general"]["video_format"] == "wmv":
            format = 1
        elif common.settings["general"]["video_format"] == "avi2":
            format = 2
        elif common.settings["general"]["video_format"] == "avi":
            format = 3
        for i in range(4):
            app_ini = app_ini.replace(
                f"videoFileFrmt={i}",
                f"videoFileFrmt={format}"
            )

        # Set the video framerate
        if common.settings["general"]["video_framerate"] == "60":
            framerate = 0
        elif common.settings["general"]["video_framerate"] == "30":
            framerate = 1
        for i in range(2):
            app_ini = app_ini.replace(
                f"videoFramerate={i}",
                f"videoFramerate={framerate}"
            )

        # Set the video resolution
        if common.settings["general"]["video_resolution"] == "1920x1080":
            resolution = 1
        elif common.settings["general"]["video_resolution"] == "1280x720":
            resolution = 2
        elif common.settings["general"]["video_resolution"] == "854x480":
            resolution = 3
        for i in range(4):
            app_ini = app_ini.replace(
                f"videoImgSize={i}",
                f"videoImgSize={resolution}"
            )

        # Write the new app.ini
        with open(os.path.join(path, "app.ini"), "w") as f:
            f.write(app_ini)
import os
import random
import threading
import time

from core import camera
from core import common
from core import commentary
from core import events


class Director:
    """Manages the overall direction of race broadcast.
    
    The Director class orchestrates the broadcast by monitoring the state of 
    the race and generating commentary. It interfaces with the iRacing SDK to 
    collect real-time data, maintains the state of drivers, detects events, and
    coordinates with the generator classes to generate commentary.
    """

    def __init__(self):
        """Initialize the Director class with necessary settings and utilities.

        Attributes:
            recording_start_time (float): Stores the time recording starts.
            events (Events): The events manager.
            commentary (Commentary): The commentary generator.
            camera (Camera): The camera manager.
        """

        # Reset race status variables
        common.race_started = False
        common.start_time = None
        common.race_time = 0
        common.all_cars_started = False

        # Reset recording start time
        common.recording_start_time = None

        # Create the events manager
        self.events = events.Events()

        # Create the commentary generator
        self.commentary = commentary.Commentary()

        # Create a variable for the camera manager (initialized when run)
        self.camera = None

        # Set running to False
        common.running = False

    def _check_all_cars_started(self):
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
        if common.race_time <= 20:
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

    def _generate_color_commentary(self):
        """Generate color commentary.

        A random chance is used to determine if color commentary should be
        generated. If the chance is met, the commentary generator is called to
        generate color commentary.
        """
        # Get the chance of generating color commentary
        chance = float(common.settings["commentary"]["color_chance"])

        # Generate color commentary with the specified chance
        if random.random() < chance:
            self.commentary.generate(
                "Add color commentary to the previous commentary.",
                None,
                "color",
                "neutral",
                yelling=True,
                rec_start_time=common.recording_start_time
            )

    def _generate_event_commentary(self, event):
        """Generate commentary for an event.

        This method generates commentary for a specified event. It also changes
        the camera to focus on the event.

        Args:
            event (dict): A dictionary containing information about the event.
        """
        # Move the camera to focus on the event
        self.camera.change_camera(event["focus"], "TV1")

        # Generate the commentary
        self.commentary.generate(
            event["description"],
            event["lap_percent"],
            "play-by-play",
            "neutral",
            common.instructions[event["type"]],
            yelling=True,
            rec_start_time=common.recording_start_time
        )

    def _update_iracing_settings(self):
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

    def run(self):
        """The main loop for the Director class.

        This method keeps running as long as the director is set to run. It
        handles all of the logic for generating commentary.
        """
        # Create the camera manager
        self.camera = camera.Camera()

        # Keep running until told to stop
        while common.running:
            # Detect if the race has started
            if common.ir["RaceLaps"] > 0 and not common.race_started:
                common.race_started = True
                common.start_time = common.ir["SessionTime"]

            # If the race has already started, update the race length
            elif common.race_started:
                common.race_time = common.ir["SessionTime"] - common.start_time

            # If the race hasn't started yet, focus on the front of the grid
            if not common.race_started:
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
            if not common.all_cars_started:
                common.all_cars_started = self._check_all_cars_started()

            # If the race has started, generate commentary
            if common.race_started and common.all_cars_started:
                # Get the next event to generate commentary for
                event = self.events.get_next_event()

                # If an event was found, report it
                if event:
                    self._generate_event_commentary(event)

                # Occasionally generate color commentary
                self._generate_color_commentary()
            
            # Wait the amount of time specified in the settings
            time.sleep(float(common.settings["system"]["director_update_freq"]))

    def start(self):
        """Start the director.

        This method starts the director by updating iRacing settings, jumping
        to the beginning of the current session, hiding the UI, starting the
        replay, and starting iRacing video capture. It then sets the running
        flag to True and starts the director thread.
        """
        # Update iRacing settings
        self._update_iracing_settings()

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
        common.recording_start_time = time.time()

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
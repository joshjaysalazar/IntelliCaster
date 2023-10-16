import irsdk
import time
from core import commentary


class Director:
    """
    Manages the overall direction of race broadcast.
    
    The Director class orchestrates the broadcast by monitoring the state of 
    the race and generating commentary. It interfaces with the iRacing SDK to 
    collect real-time data, maintains the state of drivers, detects overtakes, 
    and coordinates with the TextGenerator and VoiceGenerator classes for 
    real-time commentary.
    """

    def __init__(self, settings, add_message):
        """Initialize the Director class with necessary settings and utilities.

        Args:
            settings (ConfigParser): Settings parsed from an INI file.
            add_message (callable): A function to append messages to the
                application's message box.

        Attributes:
            settings (ConfigParser): Stores settings from the INI file.
            add_message (callable): Method to append messages.
            ir (IRSDK object): Instance for iRacing SDK.
            drivers (list): List of dictionaries to track drivers in the race.
            race_started (bool): Flag to indicate if the race has started.
            race_start_time (float): Stores the time the race starts.
            race_time (float): Stores the elapsed time since the race started.
            all_cars_started (bool): Flag to indicate if all cars have started.
            text_generator (TextGenerator object): Text-based commentary
                generator.
            voice_generator (VoiceGenerator object): Voice-based commentary
                generator.
            running (bool): Flag to control the run loop for the director.
        """
        # Member variables
        self.settings = settings
        self.add_message = add_message

        # Set up the iRacing SDK
        self.ir = irsdk.IRSDK()
        self.ir.startup()

        # Create an empty list to track drivers
        self.drivers = []

        # Track race start status
        self.race_started = False
        self.race_start_time = None
        self.race_time = 0
        self.all_cars_started = False

        # Create the commentary generators
        self.text_generator = commentary.TextGenerator(self.settings)
        self.voice_generator = commentary.VoiceGenerator(self.settings)

        # Set running to False
        self.running = False

    def check_all_cars_started(self):
        """Check if all cars in the race have started.

        This method checks if all cars have crossed the starting line and 
        started racing. It considers the race time, drivers' laps completed, and
        lap percentages.

        Returns:
            bool: True if all cars have started, False otherwise.
        """
        # If drivers list is empty, return False
        if self.drivers == []:
            return False

        # Check if race recently started
        if self.race_time <= 20:
            # Check if each car has crossed the line
            for driver in self.drivers:           
                d = driver["laps_completed"] + driver["lap_percent"]
                # If between 0.8 and 1, car hasn't started first lap
                if 0.8 < d < 1:
                    return False

        # If all cars have started, return True
        return True

    def detect_overtakes(self, prev_drivers):
        """Detect and report overtakes during the race.

        This method iterates through the current list of drivers and compares
        their positions with their positions from a previous snapshot
        (prev_drivers). If a driver has moved up in position, an overtake is
        detected and appropriate commentary is generated. The camera will also
        focus on the overtaking driver.

        Args:
            prev_drivers (list): A list of dictionaries containing the previous
                state of each driver.
                
        Note:
            Overtakes are not reported under specific conditions, like if a
            driver is in the pits, has a DNF status, or if the overtaken driver
            is not found in the current list.
        """
        # Go through all the drivers
        for driver in self.drivers:
            # Get this driver's previous information
            prev_driver = None
            for item in prev_drivers:
                if item["name"] == driver["name"]:
                    prev_driver = item
                    break

            # If a driver's position has decreased, they have overtaken someone
            if prev_driver and driver["position"] < prev_driver["position"]:
                # Find the driver whose position is 1 higher than this driver's
                overtaken = None
                for item in self.drivers:
                    if item["position"] == driver["position"] + 1:
                        overtaken = item
                        break
                
                # If no driver was found, don't report overtake
                if not overtaken:
                    continue

                # If either driver is in the pits, don't report overtake
                if driver["in_pits"] or overtaken["in_pits"]:
                    continue

                # If laps completed is negative (DNF), don't report overtake
                if driver["laps_completed"] < 0:
                    continue
                if overtaken["laps_completed"] < 0:
                    continue

                # If an legitimate overtake was found, generate the commentary
                driver_name = self.remove_numbers(driver["name"])
                overtaken_name = self.remove_numbers(overtaken["name"])
                output = (
                    f"{driver_name} has overtaken "
                    f"{overtaken_name} for "
                    f"P{driver['position']}"
                )
        
                # Move the camera to focus on the overtaking driver
                self.ir.cam_switch_num(driver["number"], 11)

                # Generate the text commentary
                commentary = self.text_generator.generate(
                    output,
                    "play-by-play",
                    "excited",
                    10,
                    "Be sure to include the position of the overtaking driver."
                )
                self.add_message(commentary)

                # Generate the voice commentary
                self.voice_generator.generate(commentary)

                # End this iteration of the loop
                break

    def remove_numbers(self, name):
        """Remove digits from a driver's name string.

        This method takes a name string that may contain digits and removes
        those digits.

        Args:
            name (str): The driver's name possibly containing digits.

        Returns:
            str: The driver's name without any digits.
        """
        # Create a list of digits
        digits = [str(i) for i in range(10)]

        # Remove any digits from the name
        for digit in digits:
            name = name.replace(digit, "")
        
        # Return the name
        return name

    def run(self):
        """The main loop for the Director class.

        This method keeps running as long as the director is set to run. It
        checks for race start, updates driver positions, detects overtakes,
        and then sleeps for the specified update frequency.
        """
        while self.running:
            # Detect if the race has started
            if self.ir["RaceLaps"] > 0 and not self.race_started:
                self.race_started = True
                self.race_start_time = self.ir["SessionTime"]

            # If the race has already started, update the race length
            elif self.race_started:
                self.race_time = self.ir["SessionTime"] - self.race_start_time

            # Store the previous state of the drivers
            prev_drivers = self.drivers.copy()

            # Update the drivers list
            self.update_drivers()

            # Check if all cars have crossed the start line if needed
            if not self.all_cars_started:
                self.all_cars_started = self.check_all_cars_started()

            # If the race has started, generate commentary
            if self.race_started and self.all_cars_started:
                # Check for overtakes
                self.detect_overtakes(prev_drivers)
            
            # Wait the amount of time specified in the settings
            time.sleep(float(self.settings["director"]["update_frequency"]))

    def update_drivers(self):
        """Update and sort the list of drivers in the race.

        This method clears the existing list of drivers and repopulates it with
        current details from the iRacing SDK. It then sorts the drivers based on
        laps completed and track position.
        
        The resulting list of drivers will contain dictionaries with details
        like name, car number, position, gap to leader, and other race-specific
        info.
        """
        # Clear the drivers list
        self.drivers = []

        # Update the drivers list
        if self.ir["CarIdxPosition"] != []:
            for i, pos in enumerate(self.ir["CarIdxPosition"]):
                # Exclude the pace car and cars that don't exist
                if pos == 0: 
                    continue
                # Exclude disconnected drivers
                if not self.ir["DriverInfo"]["Drivers"][i]["UserName"]:
                    continue

                # Add the driver to the list
                self.drivers.append(
                    {
                    "name": self.ir["DriverInfo"]["Drivers"][i]["UserName"],
                    "number": self.ir["DriverInfo"]["Drivers"][i]["CarNumber"],
                    "position": pos,
                    "gap_to_leader": self.ir["CarIdxF2Time"][i],
                    "laps_started": self.ir["CarIdxLap"][i],
                    "laps_completed": self.ir["CarIdxLapCompleted"][i],
                    "lap_percent": self.ir["CarIdxLapDistPct"][i],
                    "in_pits": self.ir["CarIdxOnPitRoad"][i],
                    "last_lap": self.ir["CarIdxLastLapTime"][i],
                    }
                )
        
        # Sort the list by laps completed + track position
        self.drivers.sort(
            key=lambda x: x["laps_completed"] + x["lap_percent"],
            reverse=True
        )

        # Update positions based on the sorted list
        for i, driver in enumerate(self.drivers):
            driver["position"] = i + 1
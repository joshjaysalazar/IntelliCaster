import irsdk
import time
from core import commentary


class Director:
    def __init__(self, settings, add_message):
        # Member variables
        self.settings = settings
        self.add_message = add_message

        # Set up the iRacing SDK
        self.ir = irsdk.IRSDK()
        self.ir.startup()

        # Create an empty list to track drivers
        self.drivers = []

        # Create the commentary generators
        self.text_generator = commentary.TextGenerator(self.settings)
        self.voice_generator = commentary.VoiceGenerator(self.settings)

        # Set running to False
        self.running = False

    def update_drivers(self):
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
                    "laps_completed": self.ir["CarIdxLapCompleted"][i],
                    "track_position": self.ir["CarIdxLapDistPct"][i],
                    "in_pits": self.ir["CarIdxOnPitRoad"][i]
                    }
                )
        
        # Sort the list by laps completed + track position
        self.drivers.sort(
            key=lambda x: x["laps_completed"] + x["track_position"],
            reverse=True
        )

        # Update positions based on the sorted list
        for i, driver in enumerate(self.drivers):
            driver["position"] = i + 1

    def detect_overtakes(self, prev_drivers):
        # Set the default output to None
        output = None

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
                
                # If there are digits in either driver's name, remove them
                driver["name"] = self.remove_numbers(driver["name"])
                overtaken["name"] = self.remove_numbers(overtaken["name"])

                # If an legitimate overtake was found, return that information
                output = (
                    f"{driver['name']} has overtaken "
                    f"{overtaken['name']} for "
                    f"P{driver['position']}"
                )
        
        if output:
            commentary = self.text_generator.generate_commentary(
                output,
                "play-by-play",
                "excited",
                10,
                "Be sure to include the position of the overtaking driver."
            )
            self.add_message(commentary)

    def remove_numbers(self, name):
        # Create a list of digits
        digits = [str(i) for i in range(10)]

        # Remove any digits from the name
        for digit in digits:
            name = name.replace(digit, "")
        
        # Return the name
        return name

    def run(self):
        while self.running:
            # Store the previous state of the drivers
            prev_drivers = self.drivers.copy()

            # Update the drivers list
            self.update_drivers()

            # Check for overtakes
            self.detect_overtakes(prev_drivers)
            
            # Wait the amount of time specified in the settings
            time.sleep(float(self.settings["director"]["update_frequency"]))

            
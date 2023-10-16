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
                    "laps_started": self.ir["CarIdxLap"][i],
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
                
                # If no driver was found, don't report the overtake
                if not overtaken:
                    continue

                # If either driver is in the pits, don't report the overtake
                if driver["in_pits"] or overtaken["in_pits"]:
                    continue

                # If laps completed is negative (DNF), don't report the overtake
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

            
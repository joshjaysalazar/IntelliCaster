from copy import deepcopy
import time

from core import common


class Events:
    """A class to detect and report events.
    
    This class is used to detect and report events such as overtakes and
    incidents. It is run in a separate thread from the main thread and is
    responsible for updating the drivers list and the previous drivers list.
    """
    def __init__(self):
        """Initialize the Events object.

        This method initializes the Events object by creating an empty events
        list and setting the id counter to 0.

        Attributes:
            events (list): A list of events
            id_counter (int): The id of the next event to be added
        """
        # Initialize the events list and id counter
        self.events = []
        self.id_counter = 0

    def _add(self, type, description, focus=None):
        """Add a new event to the list.
        
        Args:
            type (str): The type of event
            description (str): A description of the event
            focus (int): The number of the driver to focus on
        """
        # Create a new event
        new_event = {
            "id": self.id_counter,
            "type": type,
            "description": description,
            "focus": focus,
            "timestamp": time.time()
        }

        # Add the event to the list
        self.events.append(new_event)

        # Increment the id counter
        self.id_counter += 1

    def _create_drivers(self):
        """Create a list of drivers.

        This method creates a list of drivers from the iRacing SDK. It is called
        when the Events object's run method is called.

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

    def _detect_collisions(self):
        """Detect collisions and add them to the events list.
        
        This method detects collisions by comparing the current drivers list to
        the previous drivers list. If a driver's incidents have increased, they
        have collided with someone. If this is the case, the driver who was
        collided with is found and a collision event is added to the events
        list. This method also checks a few other conditions to make sure the
        collision is legitimate.
        """
        # If the race hasn't started, return
        if not common.race_started:
            return
        
        # Create an empty list of collisions
        collisions = []

        # Go through all the drivers
        for driver in common.drivers:
            # Get this driver's previous information
            prev_d = None
            for item in common.prev_drivers:
                if item["name"] == driver["name"]:
                    prev_d = item
                    break

            # Check if driver's incidents have increased by at least 4
            if prev_d and driver["incidents"] >= prev_d["incidents"] - 4:
                # If they have, add them to the list along with lap percent
                collisions.append(
                    {
                        "name": driver["name"],
                        "lap_percent": driver["lap_percent"],
                        "number": driver["number"]
                    }
                )

        print(collisions)

        # If there are no collisions, return
        if not collisions:
            return

        # Sort the list by lap percent
        collisions.sort(key=lambda x: x["lap_percent"])

        # Create a list of collisions to report
        collisions_to_report = []

        # Go through the collisions list to find collisions to report
        for i, collision in enumerate(collisions):
            # If this is the first collision, add the name and number
            if i == 0:
                collisions_to_report.append(
                    [
                        {
                            "name": collision["name"],
                            "number": collision["number"]
                        }
                    ]
                )

            # Otherwise, check if the collision is close enough to the last one
            else:
                # If it is, add the name to the last list
                lap_pct = collision["lap_percent"]
                prev_lap_pct = collisions[i - 1]["lap_percent"]
                if lap_pct - prev_lap_pct < 0.02:
                    collisions_to_report[-1].append(
                        {
                            "name": collision["name"],
                            "number": collision["number"]
                        }
                    )

                # Otherwise, add the name to a new list
                else:
                    collisions_to_report.append(
                        [
                            {
                                "name": collision["name"],
                                "number": collision["number"]
                            }
                        ]
                    )

        print(collisions_to_report)

        # # Go through the collisions to report list
        # for collision in collisions_to_report:
        #     # If there is only one driver in the collision, skip it
        #     if len(collision) == 1:
        #         continue

        #     # Get the names of the drivers involved
        #     names = []
        #     for driver in collision:
        #         names.append(common.remove_numbers(driver))

        #     # Create the description
        #     description = f"{', '.join(names)} collided"

        #     # Add the event to the list
        #     self._add("collision", description)




    def _detect_overtakes(self):
        """Detect overtakes and add them to the events list.
        
        This method detects overtakes by comparing the current drivers list to
        the previous drivers list. If a driver's position has decreased, they
        have overtaken someone. If this is the case, the driver who was
        overtaken is found and an overtake event is added to the events list.
        This method also checks a few other conditions to make sure the overtake
        is legitimate.
        """
        # Go through all the drivers
        for driver in common.drivers:
            # Get this driver's previous information
            prev_d = None
            for item in common.prev_drivers:
                if item["name"] == driver["name"]:
                    prev_d = item
                    break

            # If a driver's position has decreased, they have overtaken someone
            if prev_d and driver["position"] < prev_d["position"]:
                # Find the driver whose position is 1 higher than this driver's
                overtaken = None
                for item in common.drivers:
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

                # If an legitimate overtake was found, add it to the events list
                driver_name = common.remove_numbers(driver["name"])
                overtaken_name = common.remove_numbers(overtaken["name"])
                description = (
                    f"{driver_name} overtook "
                    f"{overtaken_name} for "
                    f"P{driver['position']}"
                )
                self._add("overtake", description, driver["number"])

                # End this iteration of the loop
                break

    def _remove(self, id):
        """Remove an event from the list.
        
        Args:
            id (int): The id of the event to remove
        """
        # Remove the event from the list
        for event in self.events:
            if event["id"] == id:
                self.events.remove(event)

    def _update_drivers(self):
        """Update the drivers list.

        This method updates the drivers list by getting the latest data from the
        iRacing SDK and updating the drivers list accordingly.
        """
        # Get driver data from iRacing SDK
        driver_data = common.ir["DriverInfo"]["Drivers"]

        # Update the drivers list
        if common.ir["CarIdxPosition"] != []:
            for i, pos in enumerate(common.ir["CarIdxPosition"]):
                # Exclude the pace car and cars that don't exist
                if pos == 0: 
                    continue
                # Exclude disconnected drivers
                try:
                    if not driver_data[i]["UserName"]:
                        continue
                # If i is out of range, continue
                except:
                    continue

                # Find the driver in the drivers list at this index
                for j, driver in enumerate(common.drivers):
                    if driver["idx"] == i:
                        # Get the driver's last lap time
                        last_lap = common.ir["CarIdxLastLapTime"][i]
                        common.drivers[j]["last_lap"] = last_lap

                        # If there's no fastest lap, set it to the last lap
                        if driver["fastest_lap"] == None:
                            common.drivers[j]["fastest_lap"] = last_lap
                        
                        # If the last lap is faster than the fastest lap, update
                        elif last_lap < driver["fastest_lap"]:
                            common.drivers[j]["fastest_lap"] = last_lap

                        # Update percentage of lap completed
                        lap_percent = common.ir["CarIdxLapDistPct"][i]
                        common.drivers[j]["lap_percent"] = lap_percent

                        # Update laps started and completed
                        started = common.ir["CarIdxLap"][i]
                        completed = common.ir["CarIdxLapCompleted"][i]
                        common.drivers[j]["laps_started"] = started
                        common.drivers[j]["laps_completed"] = completed

                        # Update gap to leader
                        gap_to_leader = common.ir["CarIdxF2Time"][i]
                        common.drivers[j]["gap_to_leader"] = gap_to_leader

                        # Update pits status
                        in_pits = common.ir["CarIdxOnPitRoad"][i]
                        common.drivers[j]["in_pits"] = in_pits

                        # Update on track status
                        if common.ir["CarIdxLapDistPct"][i] > 0:
                            common.drivers[j]["on_track"] = True
                        else:
                            common.drivers[j]["on_track"] = False

                        # Update incidents
                        incidents = driver_data[i]["CurDriverIncidentCount"]
                        common.drivers[j]["incidents"] = incidents

        # Sort the list by current position if race has started
        if common.race_started:
            common.drivers.sort(
                key=lambda x: x["laps_completed"] + x["lap_percent"],
                reverse=True
            )

            # Update the positions
            for i, driver in enumerate(common.drivers):
                common.drivers[i]["position"] = i + 1
                
        # Otherwise, sort by grid position
        else:
            common.drivers.sort(key=lambda x: x["grid_position"])

    def get_next_event(self):
        """Pick the next event to report.
        
        Returns:
            dict: The next event to report
        """
        # If there are no events, return None
        if not self.events:
            return None
        
        # Sort the events list by timestamp, with the most recent first
        self.events.sort(key=lambda x: x["timestamp"], reverse=True)

        # Return the first event in the list and remove it
        event = self.events[0]
        self._remove(event["id"])
        return event
    
    def run(self):
        """Run the events thread.

        This method runs the events thread, which detects events and adds them
        to the events list. It also updates the drivers list and the previous
        drivers list.
        """
        # Create the drivers dict
        common.drivers = self._create_drivers()

        # Keep running until told to stop
        while common.running:
            # Update the drivers list
            self._update_drivers()

            # Detect events
            self._detect_collisions()
            self._detect_overtakes()

            # Update the previous drivers list
            common.prev_drivers = deepcopy(common.drivers)

            # Remove old events
            max_hist_len = float(common.settings["system"]["event_hist_len"])
            for event in self.events:
                if time.time() - event["timestamp"] > max_hist_len:
                    self._remove(event["id"])

            # Wait the amount of time specified in the settings
            time.sleep(float(common.settings["system"]["events_update_freq"]))
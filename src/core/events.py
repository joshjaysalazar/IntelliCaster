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
        # Get the lap percent of the focused driver
        if focus != None:
            for driver in common.drivers:
                if driver["number"] == focus:
                    lap_percent = driver["lap_percent"]
                    break
        else:
            lap_percent = None

        # Create a new event
        new_event = {
            "id": self.id_counter,
            "type": type,
            "description": description,
            "lap_percent": lap_percent,
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
                    "current_lap_time": 0,
                    "fastest_lap": None,
                    "gap_to_leader": None,
                    "grid_position": quali_pos,
                    "idx": driver["CarIdx"],
                    "in_pits": False,
                    "irating": driver["IRating"],
                    "lap_distance": 0,
                    "lap_percent": 0,
                    "laps_completed": 0,
                    "laps_started": 0,
                    "lap_times": [],
                    "last_lap_time": None,
                    "last_stopped": None,
                    "license": driver["LicString"],
                    "name": driver["UserName"],
                    "number": driver["CarNumberRaw"],
                    "on_track": False,
                    "position": quali_pos,
                    "total_dist": 0
                }
            )

        # Sort the list by grid position
        driver_dict.sort(key=lambda x: x["grid_position"])

        # Return the list of drivers
        return driver_dict

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
            for d in common.prev_drivers:
                if d["name"] == driver["name"]:
                    prev_d = d
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

                # If lap percent is exactly 0, driver is likely not on track
                if driver["lap_percent"] == 0:
                    continue
                if overtaken["lap_percent"] == 0:
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

    def _detect_stopped(self):
        """Detect stopped cars and add them to the events list.
        
        This method detects stopped cars by comparing the current drivers list
        to the previous drivers list. If a driver's lap distance has not
        increased enough, they have stopped. If this is the case, an incident
        event is added to the events list.
        """
        # If the race hasn't started, don't detect stopped cars
        if not common.race_started:
            return
        
        # If not all cars have started, don't detect stopped cars
        if not common.all_cars_started:
            return
        
        # Go through all the drivers
        for driver in common.drivers:
            # Get this driver's previous information
            prev_d = None
            for d in common.prev_drivers:
                if d["name"] == driver["name"]:
                    prev_d = d
                    break

            # If total distance not increased by at least 1m, they are stopped
            if prev_d and driver["total_dist"] - prev_d["total_dist"] < 1:
                # If the driver is in the pits, don't report it
                if driver["in_pits"]:
                    continue

                # If laps completed is negative (DNF), don't report it
                if driver["laps_completed"] < 0:
                    continue

                # If lap percent is exactly 0, driver is likely not on track
                if driver["lap_percent"] == 0:
                    continue

                # If driver last stopped less than 10 seconds ago, don't report
                if driver["last_stopped"]:
                    if time.time() - driver["last_stopped"] < 10:
                        continue

                # If a legitimate stopped car was found, add it to events list
                driver_name = common.remove_numbers(driver["name"])
                description = f"{driver_name} is stopped on track"
                self._add("stopped", description, driver["number"])

                # Update the driver's last stopped time
                for i, d in enumerate(common.drivers):
                    if d["name"] == driver["name"]:
                        common.drivers[i]["last_stopped"] = time.time()
                        break

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

    def _remove_duplicates(self, events):
        """Remove events with duplicate descriptions from the list, leaving only
        the most recent event (which should be the first of its kind in the
        list).

        Args:
            events (list): A list of events
        
        Returns:
            list: A list of events with duplicates removed
        """
        # Create a new list to store the events
        new_events = []

        # Go through the events list
        for event in events:
            # If the event is not in the new list, add it
            if event["description"] in [e["description"] for e in new_events]:
                continue
            else:
                new_events.append(event)

        # Return the new list
        return new_events

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
                        # Get old last lap for later comparison
                        old_last_lap = driver["last_lap_time"]

                        # Get the driver's last lap time if it exists
                        last_lap_time = common.ir["CarIdxLastLapTime"][i]
                        if last_lap_time > 0: 
                            common.drivers[j]["last_lap_time"] = last_lap_time

                        # If there's no fastest lap, set it to the last lap
                        if driver["fastest_lap"] == None:
                            if last_lap_time > 0:
                                common.drivers[j]["fastest_lap"] = last_lap_time
                        
                        # If the last lap is faster than the fastest lap, update
                        elif last_lap_time < driver["fastest_lap"]:
                            if last_lap_time > 0:
                                common.drivers[j]["fastest_lap"] = last_lap_time
                        
                        # If new last lap different than old, append to lap list
                        if last_lap_time != old_last_lap and last_lap_time > 0:
                            common.drivers[j]["lap_times"].append(last_lap_time)

                        # Update the current lap time
                        current_lap_time = common.ir["CarIdxEstTime"][i]
                        common.drivers[j]["current_lap_time"] = current_lap_time

                        # Update percentage of lap completed
                        lap_percent = common.ir["CarIdxLapDistPct"][i]
                        common.drivers[j]["lap_percent"] = lap_percent

                        # Update laps started and completed
                        started = common.ir["CarIdxLap"][i]
                        completed = common.ir["CarIdxLapCompleted"][i]
                        common.drivers[j]["laps_started"] = started
                        common.drivers[j]["laps_completed"] = completed

                        # Update lap and total distance completed
                        track_length = common.ir["WeekendInfo"]["TrackLength"]
                        track_length = float(track_length.split(" ")[0])
                        track_length = track_length * 1000
                        lap_distance = lap_percent * track_length
                        common.drivers[j]["lap_distance"] = lap_distance
                        dist_comp = (completed * track_length) + lap_distance
                        common.drivers[j]["total_dist"] = dist_comp

                        # Update gap to leader
                        gap_to_leader = common.ir["CarIdxF2Time"][i]
                        common.drivers[j]["gap_to_leader"] = gap_to_leader

                        # Update pits status
                        track_surface = common.ir["CarIdxTrackSurface"][i]
                        if track_surface == 1 or track_surface == 2:
                            in_pits = True
                        else:
                            in_pits = False
                        common.drivers[j]["in_pits"] = in_pits

                        # Update on track status
                        if common.ir["CarIdxLapDistPct"][i] > 0:
                            common.drivers[j]["on_track"] = True
                        else:
                            common.drivers[j]["on_track"] = False

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

        # After sorting by position, update the gaps
        for i, driver in enumerate(common.drivers):
            # If the driver is the leader, gap to leader is 0
            if i == 0:
                common.drivers[i]["gap_to_leader"] = 0.

            # Otherwise, calculate the gap to leader
            else:
                # Get the leader car
                leader = common.drivers[0]
                
                # Get the leader's current lap time plus all previous laps
                leader_current = leader["current_lap_time"]
                leader_laps = sum(leader["lap_times"])
                leader_total = leader_current + leader_laps

                # Get this driver's current lap time plus all previous laps
                driver_current = driver["current_lap_time"]
                driver_laps = sum(driver["lap_times"])
                driver_total = driver_current + driver_laps

                # Calculate the gap to leader
                gap_to_leader = leader_total - driver_total

                # Update the driver's gap to leader
                common.drivers[i]["gap_to_leader"] = gap_to_leader

    def get_events(self):
        """Get the events list.
        
        Sort the events list by timestamp and remove duplicates before returning
        it.
        
        Returns:
            list: The events list
        """
        # Sort the events list by timestamp
        self.events.sort(key=lambda x: x["timestamp"], reverse=True)

        # Remove duplicate events
        self.events = self._remove_duplicates(self.events)

        # Return the events list
        return self.events
    
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
            self._detect_stopped()
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
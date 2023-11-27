import time


class Events:
    def __init__(self):
        # Initialize the events list and id counter
        self.events = []
        self.id_counter = 0

    def _add_event(self, type, description, focus=None):
        """Add a new event to the list.
        
        Args:
            type (str): The type of event
            description (str): A description of the event
            focus (str): The driver that the event is focused on
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
        self.events.insert(0, new_event)

        # Increment the id counter
        self.id_counter += 1

    def _remove_event(self, id):
        """Remove an event from the list.
        
        Args:
            id (int): The id of the event to remove
        """
        # Remove the event from the list
        for event in self.events:
            if event["id"] == id:
                self.events.remove(event)

    def detect_overtakes(self, drivers, prev_drivers):
        # Go through all the drivers
        for driver in drivers:
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
                for item in drivers:
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

                # # If an legitimate overtake was found, generate the commentary
                # driver_name = self.remove_numbers(driver["name"])
                # overtaken_name = self.remove_numbers(overtaken["name"])
                # output = (
                #     f"{driver_name} has overtaken "
                #     f"{overtaken_name} for "
                #     f"P{driver['position']}"
                # )

                # End this iteration of the loop
                break
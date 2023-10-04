import irsdk
import json


ir = irsdk.IRSDK()
ir.startup()

# Create a list of drivers
drivers = []

# Populate that list with driver info
for i, pos in enumerate(ir["CarIdxPosition"]):
    if pos == 0:
        continue
    drivers.append({
        "name": ir["DriverInfo"]["Drivers"][i]["UserName"],
        "position": pos,
        "gap_to_leader": ir["CarIdxF2Time"][i],
        "laps_completed": ir["CarIdxLapCompleted"][i],
        "car_number": ir["DriverInfo"]["Drivers"][i]["CarNumber"]
    })

print(drivers)

# Export the drivers list to a json file
with open("drivers.json", "w") as f:
    json.dump(drivers, f, indent=4)

# # Store the initial positions for all cars
# previous_positions = ir["CarIdxPosition"]

# while True:
#     # Get the position for each car
#     positions = ir["CarIdxPosition"]

#     # Compare the current positions with the previous positions
#     for i, pos in enumerate(positions):
#         if pos == 0:
#             continue
#         if pos < previous_positions[i]:
#             # Print car has overtaken
#             print(f"{ir['DriverInfo']['Drivers'][i]['UserName']} has overtaken")
    
#     # Store the current positions for the next iteration
#     previous_positions = positions
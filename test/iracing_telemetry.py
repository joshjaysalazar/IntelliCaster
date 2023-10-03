import irsdk


ir = irsdk.IRSDK()
ir.startup()

# Create an empty leaderboard
leaderboard = []

# Get the position for each car and add it to the leaderboard
positions = ir["CarIdxPosition"]
for i, pos in enumerate(positions):
    if pos == 0:
        continue
    leaderboard.append((i, pos))

# Sort the leaderboard by position
leaderboard.sort(key=lambda x: x[1])

# Print the leaderboard
for i, pos in leaderboard:
    print(f"{pos}. {ir['DriverInfo']['Drivers'][i]['UserName']}")
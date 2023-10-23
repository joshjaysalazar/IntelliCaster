import os


# Directory containing app.ini
directory = r"C:\Users\JJASalazar\Documents\iRacing"

# Read app.ini and store contents in variable
with open(os.path.join(directory, "app.ini"), "r") as f:
    app_ini = f.read()

# Replace vidCaptureEnable=0 with vidCaptureEnable=1
app_ini = app_ini.replace("vidCaptureEnable=0", "vidCaptureEnable=1")

# Replace videoCaptureMic=1 with videoCaptureMic=0
app_ini = app_ini.replace("videoCaptureMic=1", "videoCaptureMic=0")

# videoFileFrmt can be 0, 1, 2, or 3. Set it to 0
for i in range(4):
    app_ini = app_ini.replace(f"videoFileFrmt={i}", "videoFileFrmt=0")

# Set videoFramerate to 0
app_ini = app_ini.replace("videoFramerate=1", "videoFramerate=0")

# videoImgSize can also be 0-3. Set it to 1.
for i in range(4):
    app_ini = app_ini.replace(f"videoImgSize={i}", "videoImgSize=1")

# Write the new app.ini
with open(os.path.join(directory, "app.ini"), "w") as f:
    f.write(app_ini)
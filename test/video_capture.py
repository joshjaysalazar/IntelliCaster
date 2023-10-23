import irsdk
import time
from pprint import pprint

ir = irsdk.IRSDK()
ir.startup()

# Jump the beginning of current session
ir.replay_search(2)
time.sleep(1)

# Hide UI
ir.cam_set_state(8)

# Start replay
ir.replay_set_play_speed(1)

# Start internal video capture
ir.video_capture(1)

# Wait for x seconds
time.sleep(5)

# Stop internal video capture
ir.video_capture(2)

# Stop replay
ir.replay_set_play_speed(0)
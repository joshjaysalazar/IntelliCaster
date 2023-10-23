import irsdk
import time
from pprint import pprint

ir = irsdk.IRSDK()
ir.startup()

# Jump the beginning of race
ir.replay_search(0)
time.sleep(0.2)
ir.replay_search(3)
time.sleep(0.2)
ir.replay_search(3)
time.sleep(0.2)
ir.replay_search(5)
time.sleep(0.2)
ir.replay_search(5)
time.sleep(0.5)

# Hide UI
ir.cam_set_state(8)

# Start replay
ir.replay_set_play_speed(1)

# Start internal video capture
ir.video_capture(1)

# Wait for x seconds
time.sleep(20)

# Stop internal video capture
ir.video_capture(2)

# Stop replay
ir.replay_set_play_speed(0)
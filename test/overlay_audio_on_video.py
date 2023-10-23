from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
from proglog import ProgressBarLogger


# Grabbed from GitHub, can probably be made better
class CustomLogger(ProgressBarLogger):
    def callback(self, **changes):
        for (parameter, value) in changes.items():
            print (f"{value}")

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        print(f"percentage: {int(percentage)}")

# Create a custom logger instance
custom_logger = CustomLogger()

# Load the video clip
video = VideoFileClip("test/test.mp4")

# Normalize the audio
normalized_audio = audio_normalize(video.audio)

# Adjust the volume
normalized_audio = normalized_audio.fx(volumex, 0.5)

# Load additional audio clips
audio1 = AudioFileClip("test/ding.wav").set_start(3)
audio2 = AudioFileClip("test/clap.wav").set_start(6)

# Create a composite audio clip
new_audio = CompositeAudioClip([normalized_audio, audio1, audio2])

# Set the new audio to the video
video = video.set_audio(new_audio)

# Write the result to a file
video.write_videofile("output_video.mp4", codec="libx264", logger=custom_logger)

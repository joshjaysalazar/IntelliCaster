from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
import os
from proglog import ProgressBarLogger


class Editor:
    def __init__(self, settings):
        # Member variables
        self.settings = settings

    def create_video(self):
        pass

    def get_latest_video(self):
        # Get the iRacing videos folder
        path = os.path.join(self.settings["iracing"]["iracing_path"], "videos")

        # Find the most recent video in that folder
        latest_file = max(
            [os.path.join(path, f) for f in os.listdir(path)],
            key=os.path.getctime
        )

        # Return the file name
        return latest_file

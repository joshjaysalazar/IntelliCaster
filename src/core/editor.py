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
        # Look in the iRacing directory/videos directory for the latest video file
        pass
        # Return the file name

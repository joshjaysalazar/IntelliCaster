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
        # Load the video clip
        video = VideoFileClip(self.get_latest_video())

        # Normalize the original video audio
        normalized_audio = audio_normalize(video.audio)

        # Adjust the volume
        normalized_audio = normalized_audio.fx(volumex, 0.5)

    def get_latest_video(self):
        # Get the iRacing videos folder
        path = os.path.join(self.settings["iracing"]["iracing_path"], "videos")

        # Find the most recent .mp4 video in that folder
        files = []
        for file in os.listdir(path):
            if file.endswith(".mp4"):
                files.append(os.path.join(path, file))
        latest_file = max(files, key=os.path.getctime)

        # Return the file name
        return latest_file

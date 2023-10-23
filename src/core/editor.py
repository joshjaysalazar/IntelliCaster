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
        video = self.get_latest_video()

        # Normalize the original video audio
        original_audio = audio_normalize(video.audio)

        # Adjust the volume
        original_audio = original_audio.fx(volumex, 0.5)

        # Get all of the commentary audio
        commentary_audio = self.get_commentary_audio()

        # Create a composite audio clip
        new_audio = CompositeAudioClip([original_audio] + commentary_audio)

        # Set the new audio to the video
        video = video.set_audio(new_audio)

        # Write the result to a file
        video.write_videofile("output_video.mp4", codec="libx264")

    def get_commentary_audio(self):
        # Get the iRacing videos folder
        path = os.path.join(self.settings["iracing"]["iracing_path"], "videos")

        # Get a list of all of the .wav files in that folder
        files = []
        for file in os.listdir(path):
            if file.endswith(".wav"):
                files.append(os.path.join(path, file))

        audio_clips = []
        for file in files:
            # Get the file name
            file_name = os.path.basename(file)

            # Extract the timestamp from the file name
            timestamp = file_name.replace("commentary_", "")
            timestamp = timestamp.replace(".wav", "")
            timestamp = float(timestamp / 1000)

            # Create the audio clip
            audio = AudioFileClip(file).set_start(timestamp)

            # Add the audio clip to the list
            audio_clips.append(audio)

        # Return the list of audio clips
        return audio_clips

    def get_latest_video(self):
        # Get the iRacing videos folder
        path = os.path.join(self.settings["iracing"]["iracing_path"], "videos")

        # Find the most recent .mp4 video in that folder
        files = []
        for file in os.listdir(path):
            if file.endswith(".mp4"):
                files.append(os.path.join(path, file))
        latest_file = max(files, key=os.path.getctime)

        # Convert it to a MoviePy video clip
        video_clip = VideoFileClip(latest_file)

        # Return the video clip
        return video_clip

import os
import time

from customtkinter import filedialog
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from core import common
from core import export


class Editor:
    """The editor class

    This class is responsible for creating the final video. It combines the
    original video with the commentary audio clips and exports the result to a
    file.
    """

    def cleanup(self):
        """Clean up the videos folder

        Cleans up the videos folder by deleting all of the files listed in the
        intellicaster.tmp file. This is used to clean up the videos folder after
        the video has been exported.
        """
        # Get the intellicaster.tmp file path
        path = os.path.join(
            common.settings["general"]["iracing_path"],
            "videos",
            "intellicaster.tmp"
        )

        # Return if the file doesn't exist
        if not os.path.exists(path):
            return
        
        # Read the file
        with open(path, "r") as file:
            # Get the file contents
            contents = file.read()

            # Get a list of all of the files
            files = contents.split("\n")

        # Delete all of the files
        for file in files:
            # Skip empty lines
            if file == "":
                continue

            # Get the path to the file
            file_to_delete = os.path.join(
                common.settings["general"]["iracing_path"],
                "videos",
                file
            )

            # Delete the file if it exist
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)

    def _get_commentary_audio(self):
        """Get the commentary audio clips from the iRacing videos folder
        
        Returns:
            list: A list of audio clips
        """
        # Get the iRacing videos folder
        path = os.path.join(common.settings["general"]["iracing_path"], "videos")

        # Get a list of all of the .mp3 files in that folder
        files = []
        for file in os.listdir(path):
            if file.endswith(".mp3"):
                files.append(os.path.join(path, file))

        audio_clips = []
        for file in files:
            # Get the file name
            file_name = os.path.basename(file)

            # Extract the timestamp from the file name
            timestamp = file_name.replace("commentary_", "")
            timestamp = timestamp.replace(".mp3", "")
            timestamp = float(timestamp) / 1000

            # Create the audio clip
            audio = AudioFileClip(file).set_start(timestamp)

            # Cut end of audio to avoid glitch
            audio = audio.subclip(0, audio.duration - 0.05)

            # Normalize the audio
            audio = audio_normalize(audio)

            # Add the audio clip to the list
            audio_clips.append(audio)

        # Return the list of audio clips
        return audio_clips

    def _get_latest_video(self):
        """Get the latest video clip from the iRacing videos folder
        
        Returns:
            VideoFileClip: The video clip
        """
        # Get the iRacing videos folder
        path = os.path.join(
            common.settings["general"]["iracing_path"],
            "videos"
        )

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

    def create_video(self):
        """Create the video

        Creates the video by combining the original video with the commentary
        audio clips. This method is called by the main window when the user
        clicks the 'Stop Commentary' button.
        """
        # Ask the user where to save the video
        target = filedialog.asksaveasfilename(
            filetypes=[(
                "Video File",
                f"*.{common.settings['general']['video_format']}"
            )],
            initialfile="output_video",
            title="Save Video"
        )
        
        # Return if the user canceled
        if target == "":
            # Wait 3 seconds to ensure all of the files are written
            time.sleep(3)

            # Clean up videos directory
            self.cleanup()

            return

        # Create export window
        export_window = export.Export(common.app)

        # Load the video clip
        video = self._get_latest_video()

        # Normalize the original video audio
        original_audio = audio_normalize(video.audio)

        # Adjust the volume
        original_audio = original_audio.fx(volumex, 0.3)

        # Get all of the commentary audio
        commentary_audio = self._get_commentary_audio()

        # Create a composite audio clip
        new_audio = CompositeAudioClip([original_audio] + commentary_audio)

        # Set the new audio's fps to 44.1kHz (workaround MoviePy issue #863)
        new_audio = new_audio.set_fps(44100)

        # Normalize the new audio
        new_audio = audio_normalize(new_audio)

        # Set the new audio to the video
        video = video.set_audio(new_audio)

        # Write the result to a file
        video.write_videofile(
            f"{target}.{common.settings['general']['video_format']}",
            fps=int(common.settings["general"]["video_framerate"]),
            logger=export_window.progress_tracker
        )

        # Wait 3 seconds to ensure all of the files are written
        time.sleep(3)

        # Clean up videos directory
        self.cleanup()
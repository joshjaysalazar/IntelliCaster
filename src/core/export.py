import customtkinter as ctk
from proglog import ProgressBarLogger


class Export(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        # Set window properties
        self.title("Export Video")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Reposition window
        w = 540
        h = 100
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Create progress tracker object
        self.progress_tracker = ProgressTracker(self.lbl_message, self.prg_bar)

    def create_widgets(self):
        # Create message label
        self.lbl_message = ctk.CTkLabel(
            self,
            text="Preparing to export video...",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_message.pack(pady=20)

        # Create progress bar
        self.prg_bar = ctk.CTkProgressBar(
            self,
            width=500,
            orientation="horizontal"
        )
        self.prg_bar.pack(pady=(0, 20))
        self.prg_bar.set(0)

class ProgressTracker(ProgressBarLogger):
    def __init__(self, message, progress):
        super().__init__()

        # Member variables
        self.message = message
        self.progress = progress

    def bars_callback(self, bar, attr, value, old_value=None):
        # Update progress bar
        self.progress.set(value / self.bars[bar]["total"])

    def callback(self, **changes):
        for k, v in changes.items():
            text = self.format_text(v)

            # Update message label
            self.message.configure(text=text)

    def format_text(self, text):
        # Convert to string if needed
        text = str(text)

        # Remove MoviePy from text
        text = text.replace("Moviepy - ", "")
        text = text.replace("MoviePy - ", "")

        # Custom message for building video
        if text.startswith("Building video "):
            text = "Building video..."

        # Custom message for building audio
        if text.startswith("Writing audio "):
            text = "Building audio track..."

        # Custom message for done
        if text.startswith("Done"):
            text = "Done!"

        # Custom message for writing video
        if text.startswith("Writing video "):
            text = "Writing video file..."

        # Custom final message
        if text.startswith("video ready "):
            text = "Video exported successfully!"

        # Return the text
        return text
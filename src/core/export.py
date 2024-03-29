import time

import customtkinter as ctk
from proglog import ProgressBarLogger


class Export(ctk.CTkToplevel):
    """Export window

    The export window is a window that displays the progress of the video
    export. It is a child window of the main window.
    """

    def __init__(self, master):
        """Constructor for the Export window

        Args:
            master (CTk): The parent window

        Attributes:
            progress_tracker (ProgressTracker): The progress tracker object
        """
        super().__init__(master)

        # Set window properties
        self.title("Export Video")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Reposition window
        w = 540
        h = 200
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Create widgets
        self._create_widgets()

        # Create progress tracker object
        self.progress_tracker = ProgressTracker(
            self.lbl_message,
            self.prg_bar,
            self.lbl_time_remaining,
            self.btn_okay
        )

        # Bring window to front
        self.lift()

    def _create_widgets(self):
        """Create widgets for the window
        
        Creates the widgets for the window and places them in the window. This
        method is called by the constructor.
        """
        # Create message label
        self.lbl_message = ctk.CTkLabel(
            self,
            text="Preparing to export video...",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_message.pack(pady=20)

        # Create a time remaining label
        self.lbl_time_remaining = ctk.CTkLabel(
            self,
            text="Estimated time remaining: Calculating...",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_time_remaining.pack(pady=(0, 20))

        # Create progress bar
        self.prg_bar = ctk.CTkProgressBar(
            self,
            width=500,
            orientation="horizontal"
        )
        self.prg_bar.pack(pady=(0, 20))
        self.prg_bar.set(0)

        # Create disabled okay button and pack it
        self.btn_okay = ctk.CTkButton(
            self,
            text="Okay",
            state="disabled",
            command=self.destroy
        )
        self.btn_okay.pack(pady=(0, 20))

class ProgressTracker(ProgressBarLogger):
    """Progress tracker

    The progress tracker is a class that tracks the progress of the video
    export. It is used by the export window to track the progress of the export.
    """

    def __init__(self, message, progress, remaining, okay):
        """Constructor for the progress tracker

        Args:
            message (CTkLabel): The message label
            progress (CTkProgressBar): The progress bar
        """
        super().__init__()

        # Member variables
        self.message = message
        self.progress = progress
        self.remaining = remaining
        self.okay = okay

        # Keep track of the start time
        self.start_time = time.time()

    def _calculate_time_remaining(self, progress):
        """Calculate the time remaining

        Calculates the time remaining for the export. This method is called by
        the callback method.

        Args:
            progress (float): The current progress

        Returns:
            str: The time remaining
        """
        # If progress is 0, return "Calculating..."
        if progress == 0:
            return "Calculating..."

        # Calculate how long the current progress has taken
        elapsed = time.time() - self.start_time

        # Extrapolate how long the export will take
        estimated_time = elapsed / progress

        # Calculate how much time is remaining
        remaining = estimated_time - elapsed

        # Format the time remaining
        remaining = time.strftime("%H:%M:%S", time.gmtime(remaining))

        # Return the time remaining
        return remaining

    def _format_text(self, text):
        """Format text for the message label
        
        Formats the text for the message label. This method is called by the
        callback method.
        
        Args:
            text (str): The text to format
            
        Returns:
            str: The formatted text
        """
        # Convert to string if needed
        text = str(text)

        # Remove MoviePy from text
        text = text.replace("Moviepy - ", "")
        text = text.replace("MoviePy - ", "")

        # Custom message for building video
        if text.startswith("Building video "):
            text = "Building video..."

        # Custom message for building audio (also reset start time)
        if text.startswith("Writing audio "):
            self.start_time = time.time()
            text = "Building audio track..."

        # Custom message for done
        if text.startswith("Done"):
            text = "Done!"

        # Custom message for writing video (also reset start time)
        if text.startswith("Writing video "):
            self.start_time = time.time()
            text = "Exporting video file..."

        # Custom final message and active the okay button
        if text.startswith("video ready "):
            text = "Video exported successfully!"
            self.okay.configure(state="normal")

        # Return the text
        return text

    def bars_callback(self, bar, attr, value, old_value=None):
        """Callback method for the progress tracker

        This method is called by the progress tracker when the progress of the
        export changes. It updates the progress bar with the current progress.

        Args:
            bar (str): The name of the progress bar
            attr (str): The attribute that changed
            value (int): The new value of the attribute
            old_value (int, optional): The old value of the attribute. Defaults
                to None.
        """
        # Update progress bar
        total = value / self.bars[bar]["total"]
        self.progress.set(total)

        # Update time remaining label
        remaining = self._calculate_time_remaining(total)
        self.remaining.configure(text=f"Estimated time remaining: {remaining}")

    def callback(self, **changes):
        """Callback method for the progress tracker

        This method is called by the progress tracker when the progress of the
        export changes. It updates the message label with the current progress.
        
        Args:
            **changes (dict): A dictionary of changes
        """
        for k, v in changes.items():
            text = self._format_text(v)

            # Update message label
            self.message.configure(text=text)
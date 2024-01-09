import customtkinter as ctk
from proglog import ProgressBarLogger


class CancelConfirm(ctk.CTkToplevel):
    """Cancel confirmation window

    The cancel confirmation window is a window that asks the user if they want
    to cancel the video export. It is a child window of the export window.
    """

    def __init__(self, master):
        """Constructor for the Cancel Confirmation window

        Args:
            master (CTk): The parent window
        """
        super().__init__(master)

        # Set window properties
        self.title("Cancel Export")
        self.resizable(False, False)

        # Reposition window
        w = 400
        h = 170
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Create widgets
        self._create_widgets()

        # Bring window to front
        self.lift()

    def _confirm(self):
        """Confirm cancel
        
        Confirms the cancel and destroys the export window.
        """
        # Destroy export window
        self.master.destroy()

        # Destroy cancel confirmation window
        self.destroy()

    def _create_widgets(self):
        """Create widgets for the window
        
        Creates the widgets for the window and places them in the window. This
        method is called by the constructor.
        """
        # Create message label
        self.lbl_message = ctk.CTkLabel(
            self,
            text="Are you sure you want to cancel the export?",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_message.pack(pady=20)

        # Create cancel button
        self.btn_yes = ctk.CTkButton(
            self,
            text="Yes",
            command=self._confirm
        )
        self.btn_yes.pack(pady=(0, 20))

        # Create okay button
        self.btn_no = ctk.CTkButton(
            self,
            text="No",
            command=self.destroy
        )
        self.btn_no.pack(pady=(0, 20))

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

        # Reposition window
        w = 540
        h = 150
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Create widgets
        self._create_widgets()

        # Create progress tracker object
        self.progress_tracker = ProgressTracker(
            self.lbl_message,
            self.prg_bar,
            self.btn_cancel,
            self.btn_okay
        )

        # Bring window to front
        self.lift()

    def _confirm_cancel(self):
        """Confirm cancel
        
        Creates a cancel confirmation window and waits for the user to confirm
        the cancel. If the user confirms the cancel, the export window is
        destroyed by the cancel confirmation window.
        """
        # Create cancel confirmation window
        CancelConfirm(self)

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

        # Create progress bar
        self.prg_bar = ctk.CTkProgressBar(
            self,
            width=500,
            orientation="horizontal"
        )
        self.prg_bar.pack(pady=(0, 20))
        self.prg_bar.set(0)

        # Create cancel button
        self.btn_cancel = ctk.CTkButton(
            self,
            text="Cancel",
            command=self._confirm_cancel
        )
        self.btn_cancel.pack(pady=(0, 20))

        # Create hidden okay button (don't pack it until the export is done)
        self.btn_okay = ctk.CTkButton(
            self,
            text="Okay",
            command=self.destroy
        )

class ProgressTracker(ProgressBarLogger):
    """Progress tracker

    The progress tracker is a class that tracks the progress of the video
    export. It is used by the export window to track the progress of the export.
    """

    def __init__(self, message, progress, cancel, okay):
        """Constructor for the progress tracker

        Args:
            message (CTkLabel): The message label
            progress (CTkProgressBar): The progress bar
        """
        super().__init__()

        # Member variables
        self.message = message
        self.progress = progress
        self.cancel = cancel
        self.okay = okay

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

        # Custom message for building audio
        if text.startswith("Writing audio "):
            text = "Building audio track..."

        # Custom message for done
        if text.startswith("Done"):
            text = "Done!"

        # Custom message for writing video
        if text.startswith("Writing video "):
            text = "Exporting video file..."

        # Custom final message and replace cancel button with okay button
        if text.startswith("video ready "):
            text = "Video exported successfully!"
            self.cancel.pack_forget()
            self.okay.pack(pady=(0, 20))

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
        self.progress.set(value / self.bars[bar]["total"])

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
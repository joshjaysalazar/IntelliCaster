import tkinter as tk
from tkinter import PhotoImage


class SplashScreen(tk.Tk):
    def __init__(self, image_path, timeout=None):
        super().__init__()

        # Hide the window decorations
        self.overrideredirect(True)
        self.attributes('-topmost', True)

        # Load the image
        self.image = PhotoImage(file=image_path)

        # Create a label with the image
        self.image_label = tk.Label(self, image=self.image)
        self.image_label.pack()

        # Centering the window
        self.center_window()

        # Auto-close feature if timeout is set
        if timeout:
            self.after(timeout, self.destroy)

    def center_window(self):
        # Get image size
        image_width = self.image.width()
        image_height = self.image.height()

        # Centering the window with image size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (image_width / 2))
        y = int((screen_height / 2) - (image_height / 2))
        self.geometry(f"{image_width}x{image_height}+{x}+{y}")

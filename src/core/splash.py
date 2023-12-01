import tkinter as tk
from tkinter import PhotoImage


class SplashScreen(tk.Tk):
    """A splash screen for the application.
    
    This class creates a splash screen for the application. It can also
    auto-close after a given timeout.
    """
    def __init__(self, image_path, timeout=None):
        """Initialize the splash screen.

        This function initializes the splash screen by loading the image and
        creating a label with the image. It also hides the window decorations
        and centers the window on the screen.
        
        Args:
            image_path (str): The path to the image to be displayed.
            timeout (int, optional): The timeout in milliseconds. Defaults to
                None.
                
        Attributes:
            image (PhotoImage): The image to be displayed.
            image_label (tk.Label): The label containing the image.
        """
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

        # Start the main loop
        self.mainloop()

    def center_window(self):
        """Center the window on the screen.

        This function centers the window on the screen by calculating the
        center of the screen and the center of the image and then positioning
        the window accordingly.
        """
        # Get image size
        image_width = self.image.width()
        image_height = self.image.height()

        # Centering the window with image size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (image_width / 2))
        y = int((screen_height / 2) - (image_height / 2))
        self.geometry(f"{image_width}x{image_height}+{x}+{y}")

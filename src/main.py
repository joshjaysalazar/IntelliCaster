import configparser

from core.app import App
from utility.makesettings import create_settings_file


def main():
    """Entry point for the application.
    
    This function initializes the settings from an INI file, creates an instance
    of the App class, and enters the Tkinter main loop.
    """
    # Create a new settings file if it doesn't yet exist
    create_settings_file("settings.ini")

    # Load the settings file
    settings = configparser.ConfigParser()
    settings.read("settings.ini")

    # Create the app
    app = App(settings)
    app.mainloop()

if __name__ == "__main__":
    main()
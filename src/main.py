import configparser
from core.app import App


def main():
    """Entry point for the application.
    
    This function initializes the settings from an INI file, creates an instance
    of the App class, and enters the Tkinter main loop.
    """
    # Load the settings file
    settings = configparser.ConfigParser()
    settings.read("settings.ini")

    # Create the app
    app = App(settings)
    app.mainloop()

if __name__ == "__main__":
    main()
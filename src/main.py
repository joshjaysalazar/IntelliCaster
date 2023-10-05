import configparser
from core.app import App


def main():
    # Load the settings file
    settings = configparser.ConfigParser()
    settings.read("settings.ini")

    # Create the app
    app = App(settings)
    app.mainloop()

if __name__ == "__main__":
    main()
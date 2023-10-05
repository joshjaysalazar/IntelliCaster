import tomllib
from core.app import App


def main():
    # Load the settings file
    with open("settings.toml", "rb") as f:
        settings = tomllib.load(f)

    # Create the app
    app = App(settings)
    app.mainloop()

if __name__ == "__main__":
    main()
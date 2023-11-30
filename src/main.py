import threading

from core.app import App
from core import common
from core import splash


def main():
    """Entry point for the application.
    
    This function is the entry point for the application. It creates the app
    and starts the main loop.
    """
    # Create the splash screen on a separate thread
    splash_screen = splash.SplashScreen("assets/splash.png", timeout=3000)
    threading.Thread(target=splash_screen.mainloop)

    # Create the app
    common.app = App()
    common.app.mainloop()

if __name__ == "__main__":
    main()
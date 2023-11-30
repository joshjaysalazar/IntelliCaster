import threading

from core.app import App
from core import common
from core import splash


def main():
    """Entry point for the application.
    
    This function is the entry point for the application. It creates the app
    and starts the main loop. It also creates the splash screen on a separate
    thread which will be destroyed once the main window is created or after
    10 seconds, whichever comes first.
    """
    # Create the splash screen on a separate thread
    splash_screen = splash.SplashScreen("assets/splash.png", timeout=10000)
    threading.Thread(target=splash_screen.mainloop)

    # Create the app
    common.app = App(splash_screen)
    common.app.mainloop()

if __name__ == "__main__":
    main()
from core.app import App
from core import common


def main():
    """Entry point for the application.
    
    This function is the entry point for the application. It creates the app
    and starts the main loop.
    """
    # Create the app
    common.app = App()
    common.app.mainloop()

if __name__ == "__main__":
    main()
    
    
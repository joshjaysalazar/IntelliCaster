from core.app import App


def main():
    """Entry point for the application.
    
    This function is the entry point for the application. It creates the app
    and starts the main loop.
    """

    # Create the app
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
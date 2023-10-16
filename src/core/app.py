import customtkinter as ctk
import threading
from core import director


class App(ctk.CTk):
    """
    The main application class for IntelliCaster, a sim racing commentary app.
    
    This class extends ctk.CTk to create the main GUI window and functionality
    for the IntelliCaster application. It provides the user interface for
    starting and stopping the race commentary, navigating through different
    frames such as 'Home' and 'Settings', and adjusting various settings.
    """

    def __init__(self, settings):
        """Initialize the App class.

        Initializes the application window and its various components such as
        navigation and settings. Also creates an instance of the Director class.

        Args:
            settings (ConfigParser): Settings parsed from an INI file.

        Attributes:
            settings (ConfigParser): Stores settings from the INI file.
            director (Director object): Instance of the Director class to manage
                race commentary.
        """
        super().__init__()
        
        # Member variables
        self.settings = settings

        # Set window properties
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.geometry("950x500")
        self.title("IntelliCaster")

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create widgets
        self.create_navigation()
        self.create_home()
        self.create_settings()

        # Select home frame
        self.show_frame(frame="home")

        # Create the director
        self.director = director.Director(self.settings, self.add_message)

        # Add ready message
        self.add_message("Ready to start commentary...")
    
    def add_message(self, message):
        """Add a new message to the messages text box widget.
    
        Appends the given message at the top of the text box and disables 
        editing afterward.
        
        Args:
            message (str): The message to append to the text box.
        """
        self.txt_messages.configure(state="normal")
        self.txt_messages.insert("0.0", message + "\n")
        self.txt_messages.configure(state="disabled")

    def create_home(self):
        """Create the home frame and its components.
    
        Initializes a frame designated for the 'Home' tab. The frame contains
        a text box for messages and a button to start or stop the commentary.
        """
        # Create content frame
        self.frm_home = ctk.CTkFrame(
            master=self,
            corner_radius=0,
            fg_color="transparent"
        )

        # Create message box
        self.txt_messages = ctk.CTkTextbox(
            master=self.frm_home,
            width=600,
            height=300,
            state="disabled",
            wrap="word",
            font=ctk.CTkFont(size=14)
        )
        self.txt_messages.pack(padx=20, pady=20)

        # Create start/stop button
        self.btn_start_stop = ctk.CTkButton(
            master=self.frm_home,
            text="⏵ Start Commentary",
            width=300,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.start_stop
        )
        self.btn_start_stop.pack(padx=20, pady=20)

    def create_navigation(self):
        """Create the navigation frame and its components.
    
        Creates a frame that holds the navigation buttons and title label.
        Initializes and grids buttons for 'Home' and 'Settings', as well as a
        title label for the application.
        """
        # Create navigation frame
        self.frm_navigation = ctk.CTkFrame(master=self, corner_radius=0)
        self.frm_navigation.grid(row=0, column=0, sticky="nsew")
        self.frm_navigation.grid_rowconfigure(3, weight=1)

        # Create title label
        self.lbl_title = ctk.CTkLabel(
            master=self.frm_navigation,
            text="IntelliCaster",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="lightskyblue1"
        )
        self.lbl_title.grid(row=0, column=0, padx=30, pady=30)

        # Create home button
        self.btn_home = ctk.CTkButton(
            master=self.frm_navigation,
            text="Home",
            corner_radius=0,
            height=40,
            border_spacing=20,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            command=lambda: self.show_frame(frame="home")
        )
        self.btn_home.grid(row=1, column=0, sticky="ew")

        # Create settings button
        self.btn_settings = ctk.CTkButton(
            master=self.frm_navigation,
            text="Settings",
            corner_radius=0,
            height=40,
            border_spacing=20,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            command=lambda: self.show_frame(frame="settings")
        )
        self.btn_settings.grid(row=2, column=0, sticky="ew")
    
    def create_settings(self):
        """Create the settings frame and its components.
    
        Sets up a frame for the 'Settings' tab that allows users to input API
        keys, set update frequency, and define memory limits for commentary. It
        also includes a 'Save Settings' button to preserve these settings.
        """
        row = 0

        # Create content frame
        self.frm_settings = ctk.CTkScrollableFrame(
            master=self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.frm_settings.grid_columnconfigure(1, weight=1)

        # Create API keys section
        self.lbl_api_keys = ctk.CTkLabel(
            master=self.frm_settings,
            text="API Keys",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_api_keys.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=20
        )
        row += 1

        # Create API key entry boxe for OpenAI
        self.lbl_openai_key = ctk.CTkLabel(
            master=self.frm_settings,
            text="OpenAI API Key",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_openai_key.grid(
            row=row,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 20)
        )
        self.ent_openai_key = ctk.CTkEntry(
            master=self.frm_settings,
            font=ctk.CTkFont(size=14)
        )
        text = self.settings["keys"]["openai_api_key"]
        self.ent_openai_key.insert(0, text)
        self.ent_openai_key.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(0, 20),
            pady=(0, 20)
        )
        row += 1

        # Create API key entry boxe for ElevenLabs
        self.lbl_elevenlabs_key = ctk.CTkLabel(
            master=self.frm_settings,
            text="ElevenLabs API Key",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_elevenlabs_key.grid(
            row=row,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 20)
        )
        self.ent_elevenlabs_key = ctk.CTkEntry(
            master=self.frm_settings,
            font=ctk.CTkFont(size=14)
        )
        text = self.settings["keys"]["elevenlabs_api_key"]
        self.ent_elevenlabs_key.insert(0, text)
        self.ent_elevenlabs_key.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(0, 20),
            pady=(0, 20)
        )
        row += 1

        # Create Director section
        self.lbl_director = ctk.CTkLabel(
            master=self.frm_settings,
            text="Director",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_director.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=20
        )
        row += 1

        # Create update frequency entry box
        self.lbl_update_frequency = ctk.CTkLabel(
            master=self.frm_settings,
            text="Update Frequency (seconds)",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_update_frequency.grid(
            row=row,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 20)
        )
        self.ent_update_frequency = ctk.CTkEntry(
            master=self.frm_settings,
            font=ctk.CTkFont(size=14),
            width=50
        )
        text = self.settings["director"]["update_frequency"]
        self.ent_update_frequency.insert(0, text)
        self.ent_update_frequency.grid(
            row=row,
            column=1,
            sticky="w",
            padx=(0, 20),
            pady=(0, 20)
        )
        row += 1

        # Create commentary section
        self.lbl_commentary = ctk.CTkLabel(
            master=self.frm_settings,
            text="Commentary",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_commentary.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=20
        )
        row += 1

        # Create memory limit entry box
        self.lbl_memory_limit = ctk.CTkLabel(
            master=self.frm_settings,
            text="Memory Limit (messages)",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_memory_limit.grid(
            row=row,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 20)
        )
        self.ent_memory_limit = ctk.CTkEntry(
            master=self.frm_settings,
            font=ctk.CTkFont(size=14),
            width=50
        )
        text = self.settings["commentary"]["memory_limit"]
        self.ent_memory_limit.insert(0, text)
        self.ent_memory_limit.grid(
            row=row,
            column=1,
            sticky="w",
            padx=(0, 20),
            pady=(0, 20)
        )
        row += 1

        # Create save settings button
        self.btn_save_settings = ctk.CTkButton(
            master=self.frm_settings,
            text="Save Settings",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.save_settings
        )
        self.btn_save_settings.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=20
        )
        row += 1

        # Create settings saved label and hide it
        self.lbl_settings_saved = ctk.CTkLabel(
            master=self.frm_settings,
            text="Settings saved!",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_settings_saved.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20
        )
        self.lbl_settings_saved.grid_remove()
        row += 1
    
    def save_settings(self, event=None):
        """Save settings from entry boxes to a settings.ini file.

        This method gathers the settings from various entry boxes, updates the
        settings dictionary, and then saves these settings to a 'settings.ini'
        file. A message is also added to indicate that the settings have been
        saved. Additionally, a label saying 'Settings saved!' is shown for 3
        seconds.

        Args:
            event: Not used, but included for compatibility with button clicks.
        """
        # Update settings with values from entry boxes
        self.settings["keys"]["openai_api_key"] = self.ent_openai_key.get()
        self.settings["keys"]["elevenlabs_api_key"] = self.ent_elevenlabs_key.get()
        self.settings["director"]["update_frequency"] = self.ent_update_frequency.get()
        self.settings["commentary"]["memory_limit"] = self.ent_memory_limit.get()

        # Save settings to file
        with open("settings.ini", "w") as f:
            self.settings.write(f)

        # Add message
        self.add_message("Settings saved!")

        # Show settings saved label
        self.lbl_settings_saved.grid()

        # Hide settings saved label after 3 seconds
        self.after(3000, self.lbl_settings_saved.grid_remove)

    def show_frame(self, event=None, frame="home"):
        """Switch between 'Home' and 'Settings' frames and update button colors.

        Hides the current frame and shows the selected frame. Also updates the
        button colors to indicate the currently active frame.

        Args:
            event: Not used, but included for compatibility with button clicks.
            frame (str): The name of the frame to show ('home' or 'settings').
        """
        # set button color for selected button
        selected = ("gray75", "gray25")
        self.btn_home.configure(
            fg_color=selected if frame == "home" else "transparent"
        )
        self.btn_settings.configure(
            fg_color=selected if frame == "settings" else "transparent"
        )

        # Show the selected frame
        if frame == "home":
            self.frm_home.grid(row=0, column=1, sticky="nsew")
        else:
            self.frm_home.grid_forget()
        if frame == "settings":
            self.frm_settings.grid(row=0, column=1, sticky="nsew")
        else:
            self.frm_settings.grid_forget()

    def start_stop(self, event=None):
        """Toggle between starting and stopping the commentary.

        If the commentary is currently off, this method will change the button
        text to "Stop Commentary" and start the director in a separate thread.
        If the commentary is currently running, this method will change the
        button text back to "Start Commentary" and stop the director.

        Args:
            event: Not used, but included for compatibility with button clicks.
        """
        if self.btn_start_stop.cget("text") == "⏵ Start Commentary":
            # Change button text
            self.btn_start_stop.configure(text="⏹ Stop Commentary")

            # Run the director in a separate thread
            self.director.running = True
            threading.Thread(target=self.director.run).start()

            # Add message
            self.add_message("Commentary started!")

        else:
            # Change button text
            self.btn_start_stop.configure(text="⏵ Start Commentary")

            # Stop the director
            self.director.running = False

            # Add message
            self.add_message("Commentary stopped!")
import configparser
import json
from tkinter import filedialog
import threading

import customtkinter as ctk
from elevenlabs import voices
import irsdk

from core import common
from core import director
from core import editor
from utility import defaults


class App(ctk.CTk):
    """
    The main application class for IntelliCaster, a sim racing commentary app.
    
    This class extends ctk.CTk to create the main GUI window and functionality
    for the IntelliCaster application. It provides the user interface for
    starting and stopping the race commentary, navigating through different
    frames such as 'Home' and 'Settings', and adjusting various settings.
    """

    def __init__(self):
        """Initialize the App class.

        Initializes the application window and its various components such as
        navigation and settings. Also creates an instance of the Director class
        and the Editor class.

        Attributes:
            director (Director object): Instance of the Director class to manage
                race commentary.
            editor (Editor object): Instance of the Editor class to manage
        """
        super().__init__()

        # Create default files if they don't exist
        defaults.create_context_file("context.json")
        defaults.create_settings_file("settings.ini")

        # Load the settings file into common.settings
        common.settings = configparser.ConfigParser()
        common.settings.read("settings.ini")
        
        # Load context from file
        self.load_context(
            file=common.settings["system"]["context_file"],
            startup=True
        )

        # Set up the iRacing SDK
        common.ir = irsdk.IRSDK()
        common.ir.startup()

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
        self.create_context()
        self.create_settings()

        # Select home frame
        self.show_frame(frame="home")

        # Create the director
        self.director = director.Director()

        # Create the editor
        self.editor = editor.Editor()

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
        self.txt_messages.insert("end", message + "\n")
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

    def create_context(self):
        """Create the context frame and its components.

        Sets up a frame for the 'Context' tab that allows users to input
        context for the commentary. It also includes a 'Save Context' button to
        preserve these settings, and a 'Load Context' button to load context.
        """
        # Temporary variables
        self.row = 0
        self.current_section = ""

        # Create context dictionary
        self.current_context = {}

        # Create content frame
        self.frm_context = ctk.CTkScrollableFrame(
            master=self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.frm_context.grid_columnconfigure(1, weight=1)

        # Create league section
        self.create_section(
            self.frm_context,
            "league",
            "League",
            self.current_context
        )

        # Create league name entry box
        default = common.context["league"]["name"]
        self.create_entry(
            self.frm_context,
            "name",
            "Name",
            default,
            variable=self.current_context
        )

        # Create league short name entry box
        default = common.context["league"]["short_name"]
        self.create_entry(
            self.frm_context,
            "short_name",
            "Short Name",
            default,
            variable=self.current_context
        )

        # Create load context button
        self.btn_load_context = ctk.CTkButton(
            master=self.frm_context,
            text="Load Context",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.load_context
        )
        self.btn_load_context.grid(
            row=self.row,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=20
        )
        self.row += 1

        # Create save context button
        self.btn_save_context = ctk.CTkButton(
            master=self.frm_context,
            text="Save Context",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.save_context
        )
        self.btn_save_context.grid(
            row=self.row,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=20,
            pady=20
        )

        # Delete temporary variables
        del self.row
        del self.current_section

    def create_dropdown(
        self,
        master,
        name,
        text,
        options,
        default=None,
        variable={}
    ):
        """Create a dropdown for the frame.
        
        Creates a dropdown for the frame that is used to select from a list of
        options. If a default value is provided, it is selected in the dropdown.
        
        Args:
            name (str): The name of the dropdown to create.
            text (str): The text to display next to the dropdown.
            options (list): A list of options to select from.
            default (str): The default value to select in the dropdown.
            variable (dict): The dictionary to add the dropdown to.
        """

        # Create label
        lbl = ctk.CTkLabel(
            master=master,
            text=text,
            font=ctk.CTkFont(size=14)
        )

        # Grid label
        lbl.grid(
            row=self.row,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 20)
        )

        # Create dropdown
        drp = ctk.CTkOptionMenu(
            master=master,
            values=options,
            font=ctk.CTkFont(size=14)
        )

        # If default value is provided, select it in the dropdown
        if default:
            drp.set(default)

        # Grid dropdown
        drp.grid(
            row=self.row,
            column=1,
            sticky="ew",
            padx=(0, 20),
            pady=(0, 20),
            columnspan=2
        )

        # Increment row
        self.row += 1

        # Add dropdown to current settings
        variable[self.current_section][name] = drp

    def create_entry(
        self,
        master,
        name,
        text,
        default=None,
        browse=False,
        variable={}
    ):
        """Create an entry box for the frame.
        
        Creates an entry box for the frame that is used to input various
        settings. If a default value is provided, it is inserted into the entry
        box. If the browse flag is set to True, a 'Browse' button is created
        next to the entry box that allows users to browse for a directory.
        
        Args:
            name (str): The name of the entry box to create.
            text (str): The text to display next to the entry box.
            default (str): The default value to insert into the entry box.
            browse (bool): Whether or not to create a 'Browse' button.
            variable (dict): The dictionary to add the entry box to.
        """
        def browse_dir():
            """Open a file dialog to browse for a directory."""
            # Get directory
            directory = filedialog.askdirectory()

            # Insert directory into entry box
            ent.delete(0, "end")
            ent.insert(0, directory)

        # Create label
        lbl = ctk.CTkLabel(
            master=master,
            text=text,
            font=ctk.CTkFont(size=14)
        )

        # Grid label
        lbl.grid(
            row=self.row,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 20)
        )

        # Create entry box
        ent = ctk.CTkEntry(
            master=master,
            font=ctk.CTkFont(size=14)
        )

        # If default value is provided, insert it into the entry box
        if default:
            ent.insert(0, default)

        # Grid entry box
        ent.grid(
            row=self.row,
            column=1,
            sticky="ew",
            padx=(0, 20),
            pady=(0, 20),
            columnspan=1 if browse else 2
        )

        # If browse button is requested, create it
        if browse:
            btn = ctk.CTkButton(
                master=master,
                text="Browse",
                width=100,
                font=ctk.CTkFont(size=14),
                command=browse_dir
            )

            # Grid browse button
            btn.grid(
                row=self.row,
                column=2,
                sticky="ew",
                padx=(0, 20),
                pady=(0, 20)
            )

        # Increment row
        self.row += 1

        # Add entry box to current settings
        variable[self.current_section][name] = ent

    def create_navigation(self):
        """Create the navigation frame and its components.
    
        Creates a frame that holds the navigation buttons and title label.
        Initializes and grids buttons for 'Home' and 'Settings', as well as a
        title label for the application.
        """
        # Create navigation frame
        self.frm_navigation = ctk.CTkFrame(master=self, corner_radius=0)
        self.frm_navigation.grid(row=0, column=0, sticky="nsew")
        self.frm_navigation.grid_rowconfigure(4, weight=1)

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

        # Create context button
        self.btn_context = ctk.CTkButton(
            master=self.frm_navigation,
            text="Context",
            corner_radius=0,
            height=40,
            border_spacing=20,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            command=lambda: self.show_frame(frame="context")
        )
        self.btn_context.grid(row=2, column=0, sticky="ew")

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
        self.btn_settings.grid(row=3, column=0, sticky="ew")
    
    def create_section(self, master, name, text, variable={}):
        """Create a section header for the frame.
        
        Creates a section header for the frame that is used to separate
        different sections of the frame. The section header is a label with a
        bold font and a large font size.
        
        Args:
            name (str): The name of the section to create.
            text (str): The text to display in the section header.
            variable (dict): The dictionary to add the section to.
        """

        # Create label
        lbl = ctk.CTkLabel(
            master=master,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold")
        )

        # Grid label
        lbl.grid(
            row=self.row,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=20
        )

        # Increment row
        self.row += 1

        # Add section to current settings
        variable[name] = {}

        # Update current section
        self.current_section = name

    def create_settings(self):
        """Create the settings frame and its components.
    
        Sets up a frame for the 'Settings' tab that allows users to input
        settings. It also includes a 'Save Settings' button to preserve these
        settings.
        """
        # Temporary variables
        self.row = 0
        self.current_section = ""

        # Create settings dictionary
        self.current_settings = {}

        # Create content frame
        self.frm_settings = ctk.CTkScrollableFrame(
            master=self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.frm_settings.grid_columnconfigure(1, weight=1)

        # Create API keys section
        self.create_section(
            self.frm_settings,
            "keys",
            "API Keys",
            self.current_settings
        )

        # Create API key entry box for OpenAI
        default = common.settings["keys"]["openai_api_key"]
        self.create_entry(
            self.frm_settings,
            "openai_api_key",
            "OpenAI API Key",
            default,
            variable=self.current_settings
        )

        # Create API key entry box for ElevenLabs
        default = common.settings["keys"]["elevenlabs_api_key"]
        self.create_entry(
            self.frm_settings,
            "elevenlabs_api_key",
            "ElevenLabs API Key",
            default,
            variable=self.current_settings
        )

        # Create iRacing section
        self.create_section(
            self.frm_settings,
            "general",
            "General",
            self.current_settings
        )

        # Create iRacing directory entry box
        default = common.settings["general"]["iracing_path"]
        self.create_entry(
            self.frm_settings,
            "iracing_path",
            "iRacing Documents Directory",
            default,
            True,
            variable=self.current_settings
        )

        # Create the video format dropdown
        default = common.settings["general"]["video_format"]
        self.create_dropdown(
            self.frm_settings,
            "video_format",
            "Video Format",
            ["mp4", "wmv", "avi2", "avi"],
            default,
            self.current_settings
        )

        # Create the video framerate dropdown
        default = common.settings["general"]["video_framerate"]
        self.create_dropdown(
            self.frm_settings,
            "video_framerate",
            "Video Framerate",
            ["30", "60"],
            default,
            self.current_settings
        )

        # Create the video resolution dropdown
        default = common.settings["general"]["video_resolution"]
        self.create_dropdown(
            self.frm_settings,
            "video_resolution",
            "Video Resolution",
            ["1920x1080", "1280x720", "854x480"],
            default,
            self.current_settings
        )

        # Create Director section
        self.create_section(
            self.frm_settings, 
            "director",
            "Director",
            self.current_settings
        )

        # Create update frequency entry box
        default = common.settings["director"]["update_frequency"]
        self.create_entry(
            self.frm_settings,
            "update_frequency",
            "Update Frequency (seconds)",
            default,
            variable=self.current_settings
        )

        # Create commentary section
        self.create_section(
            self.frm_settings, 
            "commentary",
            "Commentary",
            self.current_settings
        )

        # Create GPT model dropdown
        default = common.settings["commentary"]["gpt_model"]
        self.create_dropdown(
            self.frm_settings,
            "gpt_model",
            "GPT Model",
            ["GPT-3.5 Turbo", "GPT-4 Turbo", "GPT-4 Turbo with Vision"],
            default,
            self.current_settings
        )
        
        # Get list of voices
        voice_list = [voice.name for voice in voices()]

        # Create play-by-play voice dropdown
        default = common.settings["commentary"]["pbp_voice"]
        self.create_dropdown(
            self.frm_settings,
            "pbp_voice",
            "Play-by-Play Voice",
            voice_list,
            default,
            self.current_settings
        )

        # Create color commentary voice dropdown
        default = common.settings["commentary"]["color_voice"]
        self.create_dropdown(
            self.frm_settings,
            "color_voice",
            "Color Commentary Voice",
            voice_list,
            default,
            self.current_settings
        )

        # Create color commentary chance entry box
        default = common.settings["commentary"]["color_chance"]
        self.create_entry(
            self.frm_settings,
            "color_chance",
            "Color Commentary Chance (%)",
            default,
            variable=self.current_settings
        )

        # Create memory limit entry box
        default = common.settings["commentary"]["memory_limit"]
        self.create_entry(
            self.frm_settings,
            "memory_limit",
            "Memory Limit (messages)",
            default,
            variable=self.current_settings
        )

        # Create save settings button
        self.btn_save_settings = ctk.CTkButton(
            master=self.frm_settings,
            text="Save Settings",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.save_settings
        )
        self.btn_save_settings.grid(
            row=self.row,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=20,
            pady=20
        )
        
        # Delete temporary variables
        del self.row
        del self.current_section
    
    def load_context(self, event=None, file=None, startup=False):
        """Load context from a context.json file.

        This method opens a file dialog to allow users to select a JSON file
        containing context for the commentary. It then loads the context from
        the file and updates the entry boxes with these settings. If a file is
        provided, it is used instead of opening a file dialog.

        Args:
            event: Not used, but included for compatibility with button clicks.
            file (str): The name of the file to load context from.
        """
        # If startup flag is set, just load the context into the dictionary
        if startup:
            # Load context from file
            with open(file, "r") as f:
                common.context = json.load(f)

            # End method
            return
        
        # Open file dialog
        if not file:
            file = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=(("JSON Files", "*.json"),)
            )

        # Check to make sure file name was provided
        if not file:
            return

        # Load context from file
        with open(file, "r") as f:
            common.context = json.load(f)

        # Update context file in settings
        common.settings["system"]["context_file"] = file

        # Save settings to file
        with open("settings.ini", "w") as f:
            common.settings.write(f)

        # Update entry boxes with context
        for key in self.current_context:
            for setting in self.current_context[key]:
                value = common.context[key][setting]
                self.current_context[key][setting].delete(0, "end")
                self.current_context[key][setting].insert(0, value)

        # Add message
        self.add_message("Context loaded!")

        # Change load context button text and color
        original_fg_color = self.btn_load_context.cget("fg_color")
        original_hover_color = self.btn_load_context.cget("hover_color")
        self.btn_load_context.configure(
            text="Context Loaded!",
            fg_color="green",
            hover_color="green"
        )

        # Change it back after 3 seconds
        self.after(
            3000,
            lambda: self.btn_load_context.configure(
                text="Load Context",
                fg_color=original_fg_color,
                hover_color=original_hover_color
            )
        )

    def save_context(self, event=None):
        """Save context from entry boxes to a JSON file.
        
        This method gathers the context from various entry boxes, updates the
        context dictionary, and then saves these settings to a JSON file. A
        message is also added to indicate that the context has been saved.
        
        Args:
            event: Not used, but included for compatibility with button clicks.
        """
        # Update context with values from entry boxes
        for key in self.current_context:
            for setting in self.current_context[key]:
                new_setting = self.current_context[key][setting].get()
                common.context[key][setting] = new_setting

        # Open save as dialog
        file_name = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON Files", "*.json"),)
        )

        # Check to make sure file name was provided
        if not file_name:
            return

        # Save context to file
        with open(file_name, "w") as f:
            json.dump(common.context, f, indent=4)

        # Update context file in settings
        common.settings["system"]["context_file"] = file_name

        # Save settings to file
        with open("settings.ini", "w") as f:
            common.settings.write(f)

        # Add message
        self.add_message("Context saved!")

        # Change save context button text and color
        original_fg_color = self.btn_save_context.cget("fg_color")
        original_hover_color = self.btn_save_context.cget("hover_color")
        self.btn_save_context.configure(
            text="Context Saved!",
            fg_color="green",
            hover_color="green"
        )

        # Change it back after 3 seconds
        self.after(
            3000,
            lambda: self.btn_save_context.configure(
                text="Save Context",
                fg_color=original_fg_color,
                hover_color=original_hover_color
            )
        )

    def save_settings(self, event=None):
        """Save settings from entry boxes to a settings.ini file.

        This method gathers the settings from various entry boxes, updates the
        settings dictionary, and then saves these settings to a 'settings.ini'
        file. A message is also added to indicate that the settings have been
        saved.

        Args:
            event: Not used, but included for compatibility with button clicks.
        """
        # Update settings with values from entry boxes
        for key in self.current_settings:
            for setting in self.current_settings[key]:
                new_setting = self.current_settings[key][setting].get()
                common.settings[key][setting] = new_setting

        # Save settings to file
        with open("settings.ini", "w") as f:
            common.settings.write(f)

        # Add message
        self.add_message("Settings saved!")

        # Change save settings button text and color
        original_fg_color = self.btn_save_settings.cget("fg_color")
        original_hover_color = self.btn_save_settings.cget("hover_color")
        self.btn_save_settings.configure(
            text="Settings Saved!",
            fg_color="green",
            hover_color="green"
        )

        # Change it back after 3 seconds
        self.after(
            3000,
            lambda: self.btn_save_settings.configure(
                text="Save Settings",
                fg_color=original_fg_color,
                hover_color=original_hover_color
            )
        )

    def show_frame(self, event=None, frame="home"):
        """Switch between frames and update button colors.

        Hides the current frame and shows the selected frame. Also updates the
        button colors to indicate the currently active frame.

        Args:
            event: Not used, but included for compatibility with button clicks.
            frame (str): The name of the frame to show.
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
        if frame == "context":
            self.frm_context.grid(row=0, column=1, sticky="nsew")
        else:
            self.frm_context.grid_forget()
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
            self.director.start()

            # Add message
            self.add_message("Commentary started!")

        else:
            # Change button text
            self.btn_start_stop.configure(text="⏵ Start Commentary")

            # Stop the director
            self.director.stop()

            # Add messages
            self.add_message("Commentary stopped!")
            self.add_message("Generating video...")

            # Create the video
            threading.Thread(target=self.editor.create_video).start()

            # Add message
            self.add_message("Video generated!")
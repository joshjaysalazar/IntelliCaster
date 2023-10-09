import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self, settings):
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

        # Add ready message
        self.add_message("Ready to start commentary...")
    
    def create_navigation(self):
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

    def create_home(self):
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
            height=150,
            state="disabled",
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
    
    def create_settings(self):
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

    def add_message(self, message):
        self.txt_messages.configure(state="normal")
        self.txt_messages.insert("0.0", message + "\n")
        self.txt_messages.configure(state="disabled")
    
    def show_frame(self, event=None, frame="home"):
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
        # Change button text
        if self.btn_start_stop.cget("text") == "⏵ Start Commentary":
            self.btn_start_stop.configure(text="⏹ Stop Commentary")
        else:
            self.btn_start_stop.configure(text="⏵ Start Commentary")

        self.add_message("Start/Stop button pressed")

    def save_settings(self, event=None):
        # Update settings with values from entry boxes
        self.settings["keys"]["openai_api_key"] = self.ent_openai_key.get()
        self.settings["keys"]["elevenlabs_api_key"] = self.ent_elevenlabs_key.get()

        # Save settings to file
        with open("settings.ini", "w") as f:
            self.settings.write(f)

        # Add message
        self.add_message("Settings saved!")

        # Show settings saved label
        self.lbl_settings_saved.grid()

        # Hide settings saved label after 3 seconds
        self.after(3000, self.lbl_settings_saved.grid_remove)
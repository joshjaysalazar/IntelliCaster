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
        # Create content frame
        self.frm_settings = ctk.CTkFrame(
            master=self,
            corner_radius=0,
            fg_color="transparent"
        )

        # Temporary label
        self.lbl_temp = ctk.CTkLabel(
            master=self.frm_settings,
            text="Settings",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.lbl_temp.pack(padx=20, pady=20)

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
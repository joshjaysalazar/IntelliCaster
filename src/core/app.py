import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self, settings):
        super().__init__()
        
        # Member variables
        self.settings = settings

        # Set window properties
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.title("IntelliCaster")

        # Create widgets
        self.create_widgets()

        # Add ready message
        self.add_message("Ready to start commentary...")

    def create_widgets(self):
        # Create title label
        self.lbl_title = ctk.CTkLabel(
            master=self,
            text="IntelliCaster",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.lbl_title.pack(padx=10, pady=10)

        # Create message box
        self.txt_messages = ctk.CTkTextbox(
            master=self,
            width=600,
            height=150,
            state="disabled",
            font=ctk.CTkFont(size=14)
        )
        self.txt_messages.pack(padx=10, pady=10)

        # Create start/stop button
        self.btn_start_stop = ctk.CTkButton(
            master=self,
            text="⏵ Start Commentary",
            width=300,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.start_stop
        )
        self.btn_start_stop.pack(padx=10, pady=10)
    
    def add_message(self, message):
        self.txt_messages.configure(state="normal")
        self.txt_messages.insert("0.0", message + "\n")
        self.txt_messages.configure(state="disabled")
    
    def start_stop(self):
        # Change button text
        if self.btn_start_stop.cget("text") == "⏵ Start Commentary":
            self.btn_start_stop.configure(text="⏹ Stop Commentary")
        else:
            self.btn_start_stop.configure(text="⏵ Start Commentary")

        self.add_message("Start/Stop button pressed")
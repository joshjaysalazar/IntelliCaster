import tkinter as tk
import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self):
        # Set window properties
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        # self.geometry("800x600")
        self.title("IntelliCaster")

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        self.lbl_title = ctk.CLabel(
            master=self,
            text="IntelliCaster",
            font=("Arial", 20)
        )
        self.lbl_title.pack()

    def run(self):
        self.mainloop()
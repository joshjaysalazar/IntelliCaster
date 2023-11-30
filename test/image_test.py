from PIL import Image
import customtkinter

def button_callback():
    print("button clicked")

app = customtkinter.CTk()
app.geometry("400x150")

my_image = customtkinter.CTkImage(light_image=Image.open("src/assets/logo_small.png"),
                                  dark_image=Image.open("src/assets/logo_small.png"),
                                  size=(300, 50))

image_label = customtkinter.CTkLabel(app, image=my_image, text="")  # display image with a CTkLabel
image_label.pack(padx=20, pady=20)

app.mainloop()
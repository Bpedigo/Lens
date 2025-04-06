import customtkinter as ctk
from src.gui import TextEditorApp

# Set the theme and color scheme
ctk.set_appearance_mode("dark")  # Modes: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "dark-blue", "green"

if __name__ == "__main__":
    app = TextEditorApp()
    app.mainloop()
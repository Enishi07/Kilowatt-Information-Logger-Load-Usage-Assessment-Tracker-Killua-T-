import customtkinter as ctk
from pages.home import HomePage
from pages.devices import DevicesPage
from pages.usage import UsagePage
from pages.records import RecordsPage
from pages.login import LoginPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class KilluaT(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Killua-T Electricity Tracker")
        self.geometry("950x600")

        # Container for switching pages
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Initialize pages dict
        self.frames = {}

        for Page in (LoginPage, HomePage, DevicesPage, UsagePage, RecordsPage):
            frame = Page(parent=self.container, controller=self)
            self.frames[Page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start at login screen
        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        # If the page defines an on_show hook, call it so pages can refresh their data
        if hasattr(frame, "on_show"):
            try:
                frame.on_show()
            except Exception:
                pass


if __name__ == "__main__":
    app = KilluaT()
    app.mainloop()

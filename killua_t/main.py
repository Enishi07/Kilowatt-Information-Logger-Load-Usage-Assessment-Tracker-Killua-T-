import customtkinter as ctk
from pages.home import HomePage
from pages.devices import DevicesPage
from pages.usage import UsagePage
from pages.records import RecordsPage
from pages.login import LoginPage
from pages.register import RegistrationPage
from pages.profile import ProfilePage

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

        # Track logged-in user
        # `current_user_id` will be set after successful login/register
        self.current_user_id = None
        self.current_username = None

        # Initialize pages dict
        self.frames = {}
        for Page in (LoginPage, RegistrationPage, HomePage, DevicesPage, UsagePage, RecordsPage, ProfilePage):
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
        # Load two sizes: a small avatar for top-bars and a large one
        # for the Profile page. This prevents the small image from
        # being applied to the large profile widget (causing it to look tiny).
        try:
            from pages.assets import load_image, clear_image_cache
            
            img_small = None
            img_large = None
            uid = getattr(self, 'current_user_id', None)
            
            if uid:
                cursor = __import__('database.db', fromlist=['cursor']).cursor
                cursor.execute("SELECT profile_pic FROM users WHERE id = ?", (uid,))
                row = cursor.fetchone()
                profile_pic = row[0] if row else None
                
                if profile_pic:
                    try:
                        img_small = load_image(profile_pic, size=(28, 28), circle=True)
                    except Exception:
                        img_small = None
                    try:
                        img_large = load_image(profile_pic, size=(180, 180), circle=True)
                    except Exception:
                        img_large = None

            # Propagate or clear image on frames regardless of whether uid is set.
            for f in self.frames.values():
                # handle small top-bar avatar
                if hasattr(f, 'profile_pic_lbl'):
                    try:
                        w = f.profile_pic_lbl
                        if img_small:
                            w.configure(image=img_small, text='')
                            w.image = img_small
                        else:
                            try:
                                w.configure(image=None, text='')
                            except Exception:
                                try:
                                    w.configure(text='')
                                except Exception:
                                    pass
                            try:
                                if hasattr(w, 'image'):
                                    del w.image
                            except Exception:
                                try:
                                    delattr(w, 'image')
                                except Exception:
                                    pass
                    except Exception:
                        pass

                # handle large profile page avatar
                if hasattr(f, 'img_label'):
                    try:
                        w = f.img_label
                        if img_large:
                            w.configure(image=img_large, text='')
                            w.image = img_large
                        else:
                            try:
                                w.configure(image=None, text='')
                            except Exception:
                                try:
                                    w.configure(text='')
                                except Exception:
                                    pass
                            try:
                                if hasattr(w, 'image'):
                                    del w.image
                            except Exception:
                                try:
                                    delattr(w, 'image')
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception:
            pass


if __name__ == "__main__":
    app = KilluaT()
    app.mainloop()

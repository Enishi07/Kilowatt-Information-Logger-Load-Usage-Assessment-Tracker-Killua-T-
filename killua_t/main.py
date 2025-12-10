import customtkinter as ctk
from pages.home import HomePage
from pages.devices import DevicesPage
from pages.usage import UsagePage
from pages.records import RecordsPage
from pages.meralco_rate import MeralcoRatePage
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
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Track logged-in user
        # `current_user_id` will be set after successful login/register
        self.current_user_id = None
        self.current_username = None
        self._last_profile_pic = None  # Track previous profile_pic to detect changes

        # Initialize pages dict
        self.frames = {}
        for Page in (LoginPage, RegistrationPage, HomePage, DevicesPage, UsagePage, RecordsPage, MeralcoRatePage, ProfilePage):
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
            from pages.assets import load_image, create_placeholder_image, clear_placeholder_cache
            
            img_small = None
            img_large = None
            uid = getattr(self, 'current_user_id', None)
            print(f"[show_frame] uid={uid}")
            
            if uid:
                cursor = __import__('database.db', fromlist=['cursor']).cursor
                cursor.execute("SELECT profile_pic FROM users WHERE id = ?", (uid,))
                row = cursor.fetchone()
                profile_pic = row[0] if row else None
                print(f"[show_frame] profile_pic={repr(profile_pic)}")
                
                # Detect if profile_pic changed (e.g., from user with pic to user without)
                profile_pic_changed = (profile_pic != self._last_profile_pic)
                self._last_profile_pic = profile_pic
                print(f"[show_frame] profile_pic_changed={profile_pic_changed}")
                
                # Clear placeholder cache if switching between users
                if profile_pic_changed:
                    clear_placeholder_cache()
                    print(f"[show_frame] cleared placeholder cache")
                
                if profile_pic:
                    try:
                        img_small = load_image(profile_pic, size=(28, 28), circle=True)
                        img_large = load_image(profile_pic, size=(180, 180), circle=True)
                        print(f"[show_frame] loaded real images")
                    except Exception as e:
                        print(f"[show_frame] error loading real images: {e}")
                        img_small = None
                        img_large = None
                else:
                    # Get cached placeholder images (reuse, don't recreate)
                    img_small = create_placeholder_image(size=(28, 28), text="")
                    img_large = create_placeholder_image(size=(180, 180), text="No Image")
                    print(f"[show_frame] created placeholder images")

            # Only update images if they actually changed (profile_pic_changed=True or uid is None)
            should_update_images = profile_pic_changed if uid else True
            
            if should_update_images:
                print(f"[show_frame] updating images on all frames")
                # Propagate or clear image on frames
                for f in self.frames.values():
                    # handle small top-bar avatar
                    if hasattr(f, 'profile_pic_lbl'):
                        try:
                            w = f.profile_pic_lbl
                            # Clear old image completely using empty string
                            w.configure(image="", text='')
                            # Don't delete the attribute - just let it be reassigned
                            
                            # Set new image
                            if img_small:
                                w.configure(image=img_small, text='')
                                w.image = img_small
                                print(f"[show_frame] set img_small on profile_pic_lbl")
                            else:
                                print(f"[show_frame] cleared profile_pic_lbl")
                        except Exception as e:
                            print(f"[show_frame] error with profile_pic_lbl: {e}")

                    # handle large profile page avatar
                    if hasattr(f, 'img_label'):
                        try:
                            w = f.img_label
                            # Clear old image completely using empty string
                            w.configure(image="", text='')
                            # Don't delete the attribute - just let it be reassigned
                            
                            # Set new image
                            if img_large:
                                w.configure(image=img_large, text='')
                                w.image = img_large
                                print(f"[show_frame] set img_large on img_label")
                            else:
                                print(f"[show_frame] cleared img_label")
                        except Exception as e:
                            print(f"[show_frame] error with img_label: {e}")
        except Exception as e:
            print(f"[show_frame] outer exception: {e}")


if __name__ == "__main__":
    app = KilluaT()
    app.mainloop()

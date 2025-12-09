import customtkinter as ctk
from database import db as _db
from .assets import get_logo


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Top bar with menu and title
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30)
        menu_btn.pack(side="left", padx=10)

        # Title with logo
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=6)
        logo_img = get_logo((28, 28))
        if logo_img:
            logo_lbl = ctk.CTkLabel(title_frame, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))
        title = ctk.CTkLabel(title_frame, text="Killua-T", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Username label (will be updated in on_show)
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 10))
        self.user_label.pack(side="right", padx=10)

        # Show current DB backend (SQLite or MySQL)
        try:
            db_type = getattr(_db, 'DB_TYPE', 'sqlite')
        except Exception:
            db_type = 'sqlite'

            # Right-side profile area (profile pic + DB label)
            right_top = ctk.CTkFrame(top, fg_color="transparent")
            right_top.pack(side="right", padx=10)

            # DB label
            db_label = ctk.CTkLabel(right_top, text=f"DB: {db_type}", font=("Arial", 10))
            db_label.pack(side="right", padx=6)

            # Profile picture placeholder will be updated in on_show
            self.profile_pic_lbl = ctk.CTkLabel(right_top, text="", width=28, height=28)
            self.profile_pic_lbl.pack(side="right", padx=6)

        # Main content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=30, pady=10)

        left_col = ctk.CTkFrame(content, width=220, fg_color="transparent")
        left_col.pack(side="left", anchor="n", padx=(10, 40), pady=20)

        # Action buttons styled similar to the design
        btn_devices = ctk.CTkButton(left_col, text="Add Electronic Device",
                        width=180, command=lambda: controller.show_frame("DevicesPage"))
        btn_devices.pack(pady=12)

        btn_usage = ctk.CTkButton(left_col, text="Your Daily Usage",
                      width=180, command=lambda: controller.show_frame("UsagePage"))
        btn_usage.pack(pady=12)

        btn_records = ctk.CTkButton(left_col, text="View Records",
                        width=180, command=lambda: controller.show_frame("RecordsPage"))
        btn_records.pack(pady=12)

        # Profile button and logout below it
        btn_profile = ctk.CTkButton(left_col, text="Profile",
                        width=180, command=lambda: controller.show_frame("ProfilePage"))
        btn_profile.pack(pady=12)

        btn_logout = ctk.CTkButton(left_col, text="Logout", width=180, command=lambda: [setattr(controller, 'current_user_id', None), setattr(controller, 'current_username', None), controller.show_frame('LoginPage')])
        btn_logout.pack(pady=12)

        # Right column: summary / recent entries
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, pady=20)

        rate_label = ctk.CTkLabel(right_col, text="Current MERALCO Rate: 12.64 PHP / kWh",
                                  font=("Arial", 14))
        rate_label.pack(pady=(30, 10))

        recent_title = ctk.CTkLabel(right_col, text="Recent Entries (Preview):",
                                    text_color="#c62828", font=("Arial", 12, "bold"))
        recent_title.pack(pady=(10, 6))

        preview = ctk.CTkLabel(right_col, text="- Laptop: 2.5 hours → 0.25 kWh → ₱3.16\n- Aircon: 1 hour → 1.00 kWh → ₱12.64",
                                justify="left", font=("Arial", 12))
        preview.pack(anchor="w")

    def on_show(self):
        # Update displayed username when page is shown
        try:
            uid = getattr(self.controller, 'current_user_id', None)
            uname = getattr(self.controller, 'current_username', None)
            # update profile pic label and username
            if uid:
                try:
                    from .assets import load_image
                    cursor = __import__('database.db', fromlist=['cursor']).cursor
                    cursor.execute("SELECT profile_pic FROM users WHERE id = ?", (uid,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        img = load_image(row[0], size=(28, 28), circle=True)
                        if img:
                            self.profile_pic_lbl.configure(image=img, text='')
                            self.profile_pic_lbl.image = img
                    else:
                        # No profile image for this user -> clear previous image
                        try:
                            self.profile_pic_lbl.configure(image=None, text='')
                        except Exception:
                            try:
                                self.profile_pic_lbl.configure(text='')
                            except Exception:
                                pass
                        try:
                            if hasattr(self.profile_pic_lbl, 'image'):
                                del self.profile_pic_lbl.image
                        except Exception:
                            pass
                        try:
                            if hasattr(self.profile_pic_lbl, 'image'):
                                del self.profile_pic_lbl.image
                        except Exception:
                            pass
                except Exception:
                    pass
            # update textual user label
            if uname:
                self.user_label.configure(text=f"User: {uname}")
            else:
                self.user_label.configure(text="Not logged in")
        except Exception:
            pass

    def logout(self):
        # Clear controller user state and return to login page
        try:
            self.controller.current_user_id = None
            self.controller.current_username = None
        except Exception:
            pass
        self.controller.show_frame("LoginPage")

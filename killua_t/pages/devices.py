import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor
from .assets import get_logo
from .sidebar import Sidebar


class DevicesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sidebar = None
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30, command=self.show_menu)
        menu_btn.pack(side="left", padx=10)

        # Title with logo
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=6)
        logo_img = get_logo((36, 36))
        if logo_img:
            logo_lbl = ctk.CTkLabel(title_frame, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))
        title = ctk.CTkLabel(title_frame, text="Add / Manage Devices", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Right side: username and profile pic
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 16, "bold"))
        self.user_label.pack(side="right", padx=10)

        # profile pic placeholder on right
        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
        self.profile_pic_lbl.pack(side="right", padx=6)

        # Body layout
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=10)

        form = ctk.CTkFrame(body, fg_color="transparent")
        form.pack(anchor="n", pady=10)

        label_name = ctk.CTkLabel(form, text="Device Name:", anchor="w", font=("Arial", 14))
        label_name.grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.entry_name = ctk.CTkEntry(form, placeholder_text="Device Name", width=360)
        self.entry_name.grid(row=0, column=1, padx=6, pady=6)

        label_watt = ctk.CTkLabel(form, text="Device Stable Wattage:", anchor="w", font=("Arial", 14))
        label_watt.grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.entry_watt = ctk.CTkEntry(form, placeholder_text="Stable Wattage (W)", width=360)
        self.entry_watt.grid(row=1, column=1, padx=6, pady=6)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=2, column=1, pady=12)

        add_btn = ctk.CTkButton(actions, text="Add Device", width=120, command=self.add_device, fg_color="#4CAF50", hover_color="#45a049")
        add_btn.pack(side="left", padx=8)

        clear_btn = ctk.CTkButton(actions, text="Clear", width=100, command=self.clear_form)
        clear_btn.pack(side="left", padx=8)

        list_label = ctk.CTkLabel(body, text="Device List:", anchor="w", font=("Arial", 14, "bold"))
        list_label.pack(anchor="w", pady=(14, 6))

        self.device_list = ctk.CTkTextbox(body, width=700, height=240)
        self.device_list.pack(pady=6)

        self.refresh_devices()

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_watt.delete(0, "end")

    def add_device(self):
        name = self.entry_name.get()
        watt = self.entry_watt.get()

        if not name or not watt:
            return messagebox.showerror("Error", "Please fill all fields.")

        # associate device with current user (if any); allow NULL for shared devices
        user_id = self.controller.current_user_id
        cursor.execute("INSERT INTO devices (name, watt_per_hour, user_id) VALUES (?, ?, ?)",
                   (name, float(watt), user_id))
        conn.commit()

        self.refresh_devices()
        self.clear_form()

    def refresh_devices(self):
        # show devices for the current user and shared devices (user_id IS NULL)
        user_id = self.controller.current_user_id
        if user_id:
            cursor.execute("SELECT name, watt_per_hour FROM devices WHERE user_id = ? OR user_id IS NULL", (user_id,))
        else:
            cursor.execute("SELECT name, watt_per_hour FROM devices WHERE user_id IS NULL")
        rows = cursor.fetchall()

        self.device_list.delete("1.0", "end")
        for name, watt in rows:
            self.device_list.insert("end", f"{name} — {watt} W\n")

    def on_show(self):
        # Refresh when the page becomes visible
        # (image loading is handled by main.show_frame, so don't load images here)
        try:
            uname = getattr(self.controller, 'current_username', None)
            if uname:
                self.user_label.configure(text=uname)
            else:
                self.user_label.configure(text="Not logged in")
            self.refresh_devices()
        except Exception:
            pass

    def show_menu(self):
        """Show sidebar menu."""
        if self.sidebar is None or not self.sidebar.winfo_exists():
            self.sidebar = Sidebar(self, self.controller, on_close=lambda: setattr(self, 'sidebar', None))


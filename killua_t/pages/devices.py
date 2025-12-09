import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor


class DevicesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30)
        menu_btn.pack(side="left", padx=10)

        title = ctk.CTkLabel(top, text="Add / Manage Devices", font=("Arial", 20, "bold"))
        title.pack(side="top")

        back_btn = ctk.CTkButton(top, text="Back",
                                 width=80, command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(side="right", padx=12)

        # Body layout
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=10)

        form = ctk.CTkFrame(body, fg_color="transparent")
        form.pack(anchor="n", pady=10)

        label_name = ctk.CTkLabel(form, text="Device Name:", anchor="w")
        label_name.grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.entry_name = ctk.CTkEntry(form, placeholder_text="Device Name", width=360)
        self.entry_name.grid(row=0, column=1, padx=6, pady=6)

        label_watt = ctk.CTkLabel(form, text="Watt per Hour:", anchor="w")
        label_watt.grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.entry_watt = ctk.CTkEntry(form, placeholder_text="Watt Per Hour (W)", width=360)
        self.entry_watt.grid(row=1, column=1, padx=6, pady=6)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=2, column=1, pady=12)

        add_btn = ctk.CTkButton(actions, text="Add Device", width=120, command=self.add_device)
        add_btn.pack(side="left", padx=8)

        clear_btn = ctk.CTkButton(actions, text="Clear", width=100, command=self.clear_form)
        clear_btn.pack(side="left", padx=8)

        list_label = ctk.CTkLabel(body, text="Device List:", anchor="w", font=("Arial", 12, "bold"))
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

        cursor.execute("INSERT INTO devices (name, watt_per_hour) VALUES (?, ?)",
                       (name, float(watt)))
        conn.commit()

        self.refresh_devices()
        self.clear_form()

    def refresh_devices(self):
        cursor.execute("SELECT name, watt_per_hour FROM devices")
        rows = cursor.fetchall()

        self.device_list.delete("1.0", "end")
        for name, watt in rows:
            self.device_list.insert("end", f"{name} — {watt} W\n")

    def on_show(self):
        # Refresh when the page becomes visible
        try:
            self.refresh_devices()
        except Exception:
            pass

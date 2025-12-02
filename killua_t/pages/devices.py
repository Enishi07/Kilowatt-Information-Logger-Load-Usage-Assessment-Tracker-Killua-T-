import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor


class DevicesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="Manage Devices", font=("Arial", 25, "bold"))
        title.pack(pady=20)

        # Input fields
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Device Name")
        self.entry_name.pack(pady=10)

        self.entry_watt = ctk.CTkEntry(self, placeholder_text="Watt Per Hour (W)")
        self.entry_watt.pack(pady=10)

        add_btn = ctk.CTkButton(self, text="Add Device", command=self.add_device)
        add_btn.pack(pady=10)

        back_btn = ctk.CTkButton(self, text="Back to Menu",
                                 command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(pady=20)

        self.device_list = ctk.CTkTextbox(self, width=600, height=300)
        self.device_list.pack(pady=20)

        self.refresh_devices()

    def add_device(self):
        name = self.entry_name.get()
        watt = self.entry_watt.get()

        if not name or not watt:
            return messagebox.showerror("Error", "Please fill all fields.")

        cursor.execute("INSERT INTO devices (name, watt_per_hour) VALUES (?, ?)",
                       (name, float(watt)))
        conn.commit()

        self.refresh_devices()
        self.entry_name.delete(0, "end")
        self.entry_watt.delete(0, "end")

    def refresh_devices(self):
        cursor.execute("SELECT name, watt_per_hour FROM devices")
        rows = cursor.fetchall()

        self.device_list.delete("1.0", "end")
        for name, watt in rows:
            self.device_list.insert("end", f"{name} — {watt} W\n")

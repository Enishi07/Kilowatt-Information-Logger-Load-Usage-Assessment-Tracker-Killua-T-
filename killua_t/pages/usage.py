import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor


MERALCO_RATE = 12.64


class UsagePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="Daily Usage Calculator",
                             font=("Arial", 25, "bold"))
        title.pack(pady=20)

        # Device selection combo
        self.device_var = ctk.StringVar()
        self.combo = ctk.CTkComboBox(self, variable=self.device_var,
                                     values=self.load_devices())
        self.combo.pack(pady=10)

        self.entry_duration = ctk.CTkEntry(self, placeholder_text="Duration (minutes)")
        self.entry_duration.pack(pady=10)

        calc_btn = ctk.CTkButton(self, text="Calculate Usage",
                                 command=self.calculate_usage)
        calc_btn.pack(pady=10)

        back_btn = ctk.CTkButton(self, text="Back to Menu",
                                 command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(pady=15)

        self.result = ctk.CTkTextbox(self, width=600, height=300)
        self.result.pack(pady=20)

    def load_devices(self):
        cursor.execute("SELECT name FROM devices")
        return [row[0] for row in cursor.fetchall()]

    def calculate_usage(self):
        device_name = self.device_var.get()
        duration = self.entry_duration.get()

        if not device_name or not duration:
            return messagebox.showerror("Error", "Please complete all fields.")

        cursor.execute("SELECT watt_per_hour FROM devices WHERE name = ?", (device_name,))
        watt = cursor.fetchone()[0]

        minutes = float(duration)
        hours = minutes / 60
        kwh = (watt * hours) / 1000
        cost = kwh * MERALCO_RATE

        self.result.delete("1.0", "end")
        self.result.insert("end", f"Device: {device_name}\n")
        self.result.insert("end", f"Watt/hour: {watt}W\n")
        self.result.insert("end", f"Duration: {minutes} min\n")
        self.result.insert("end", f"Total kWh: {kwh:.4f}\n")
        self.result.insert("end", f"Estimated Cost: ₱{cost:.2f}\n")

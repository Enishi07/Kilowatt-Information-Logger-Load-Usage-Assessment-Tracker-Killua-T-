import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor
from datetime import datetime


MERALCO_RATE = 12.64


class UsagePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30)
        menu_btn.pack(side="left", padx=10)

        title = ctk.CTkLabel(top, text="Daily Usage Calculator", font=("Arial", 20, "bold"))
        title.pack(side="top")

        back_btn = ctk.CTkButton(top, text="Back", width=80,
                                 command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(side="right", padx=12)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=10)

        left = ctk.CTkFrame(body, width=420, fg_color="transparent")
        left.pack(side="left", padx=(10, 30), pady=10)

        # Device selection combo
        self.device_var = ctk.StringVar()
        self.combo = ctk.CTkComboBox(left, variable=self.device_var,
                                     values=self.load_devices(), width=300)
        self.combo.pack(pady=8)

        self.entry_duration = ctk.CTkEntry(left, placeholder_text="Duration (minutes)")
        self.entry_duration.pack(pady=8)

        calc_btn = ctk.CTkButton(left, text="Add to List", width=160,
                                 command=self.calculate_usage)
        calc_btn.pack(pady=12)

        # Results / today's list
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, pady=10)

        self.result = ctk.CTkTextbox(right, width=500, height=320)
        self.result.pack(pady=8)

    def load_devices(self):
        cursor.execute("SELECT name FROM devices")
        return [row[0] for row in cursor.fetchall()]

    def on_show(self):
        # Refresh the device list each time the page is shown (handles runtime DB changes)
        try:
            devices = self.load_devices()
            self.combo.configure(values=devices)
        except Exception:
            pass

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

        # Display calculation in the UI
        self.result.delete("1.0", "end")
        self.result.insert("end", f"Device: {device_name}\n")
        self.result.insert("end", f"Watt/hour: {watt}W\n")
        self.result.insert("end", f"Duration: {minutes} min\n")
        self.result.insert("end", f"Total kWh: {kwh:.4f}\n")
        self.result.insert("end", f"Estimated Cost: ₱{cost:.2f}\n")

        # Persist the calculation as a record and record_item so RecordsPage can display it
        try:
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO records (date, total_kwh, total_cost) VALUES (?, ?, ?)",
                (today, kwh, cost)
            )
            # lastrowid should be available on both sqlite and mysql connector cursors
            record_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO record_items (record_id, device_name, watt_per_hour, duration_minutes, kwh_used, cost) VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, device_name, watt, minutes, kwh, cost)
            )

            conn.commit()
            messagebox.showinfo("Saved", "Calculation saved to records.")
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("DB Error", f"Failed to save record: {e}")

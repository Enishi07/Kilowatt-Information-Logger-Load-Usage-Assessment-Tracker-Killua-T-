import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor, get_current_rate
from datetime import datetime
from .assets import get_logo
from .sidebar import Sidebar


class UsagePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sidebar = None
        self.current_rate = get_current_rate()
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
        title = ctk.CTkLabel(title_frame, text="Daily Usage Calculator", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Right-side username and profile pic for all pages (updated in on_show)
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 16, "bold"))
        self.user_label.pack(side="right", padx=10)

        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
        self.profile_pic_lbl.pack(side="right", padx=6)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=10)

        left = ctk.CTkFrame(body, width=420, fg_color="transparent")
        left.pack(side="left", padx=(10, 30), pady=10)

        # Device selection label and combo
        device_label = ctk.CTkLabel(left, text="Select Device:", font=("Arial", 13), anchor="w")
        device_label.pack(anchor="w", pady=(8, 4))
        
        self.device_var = ctk.StringVar()
        self.combo = ctk.CTkComboBox(left, variable=self.device_var,
                                     values=self.load_devices(), width=300)
        self.combo.pack(pady=(0, 8))

        # Hours input
        hours_label = ctk.CTkLabel(left, text="Hours:", font=("Arial", 13), anchor="w")
        hours_label.pack(anchor="w", pady=(8, 4))
        
        self.entry_hours = ctk.CTkEntry(left, placeholder_text="0", width=300)
        self.entry_hours.pack(pady=(0, 8))

        # Minutes input
        minutes_label = ctk.CTkLabel(left, text="Minutes:", font=("Arial", 13), anchor="w")
        minutes_label.pack(anchor="w", pady=(8, 4))
        
        self.entry_minutes = ctk.CTkEntry(left, placeholder_text="0", width=300)
        self.entry_minutes.pack(pady=(0, 8))

        calc_btn = ctk.CTkButton(left, text="Add to List", width=160,
                                 command=self.calculate_usage, fg_color="#4CAF50", hover_color="#45a049")
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
            uname = getattr(self.controller, 'current_username', None)
            if uname:
                self.user_label.configure(text=uname)
            else:
                self.user_label.configure(text="Not logged in")
            self.current_rate = get_current_rate()
            devices = self.load_devices()
            self.combo.configure(values=devices)
        except Exception:
            pass

    def show_menu(self):
        """Show sidebar menu."""
        if self.sidebar is None or not self.sidebar.winfo_exists():
            self.sidebar = Sidebar(self, self.controller, on_close=lambda: setattr(self, 'sidebar', None))

    def calculate_usage(self):
        device_name = self.device_var.get()
        hours_str = self.entry_hours.get().strip()
        minutes_str = self.entry_minutes.get().strip()

        if not device_name:
            return messagebox.showerror("Error", "Please select a device.")

        # Parse hours and minutes (default to 0 if empty)
        try:
            hours_val = float(hours_str) if hours_str else 0.0
            minutes_val = float(minutes_str) if minutes_str else 0.0
        except ValueError:
            return messagebox.showerror("Error", "Please enter valid numbers for hours and minutes.")

        # Check if at least one is provided
        if hours_val == 0 and minutes_val == 0:
            return messagebox.showerror("Error", "Please enter hours and/or minutes.")

        cursor.execute("SELECT watt_per_hour FROM devices WHERE name = ?", (device_name,))
        result = cursor.fetchone()
        if not result:
            return messagebox.showerror("Error", "Device not found.")
        watt = result[0]

        # Convert to total minutes
        total_minutes = (hours_val * 60) + minutes_val
        hours = total_minutes / 60
        kwh = (watt * hours) / 1000
        rate = self.current_rate or get_current_rate()
        cost = kwh * rate

        # Display calculation in the UI
        self.result.delete("1.0", "end")
        self.result.insert("end", f"Device: {device_name}\n")
        self.result.insert("end", f"Stable Wattage: {watt}W\n")
        self.result.insert("end", f"Duration: {hours_val:.0f}h {minutes_val:.0f}min ({total_minutes:.0f} min total)\n")
        self.result.insert("end", f"Total kWh: {kwh:.4f}\n")
        self.result.insert("end", f"Rate used: ₱{rate:.2f} / kWh\n")
        self.result.insert("end", f"Estimated Cost: ₱{cost:.2f}\n")

        # Persist the calculation as a record and record_item so RecordsPage can display it
        try:
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = self.controller.current_user_id
            cursor.execute(
                "INSERT INTO records (date, total_kwh, total_cost, user_id) VALUES (?, ?, ?, ?)",
                (today, kwh, cost, user_id)
            )
            # lastrowid should be available on both sqlite and mysql connector cursors
            record_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO record_items (record_id, device_name, watt_per_hour, duration_minutes, kwh_used, cost) VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, device_name, watt, total_minutes, kwh, cost)
            )

            conn.commit()
            messagebox.showinfo("Saved", "Calculation saved to records.")
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("DB Error", f"Failed to save record: {e}")

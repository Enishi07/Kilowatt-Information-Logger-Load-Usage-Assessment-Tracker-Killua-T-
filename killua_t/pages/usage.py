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
        self.daily_entries = []  # Store entries for the day before confirming
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
        left.pack(side="left", padx=(10, 30), pady=10, fill="both", expand=False)

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

        # Add to list button
        add_btn = ctk.CTkButton(left, text="Add Device to List", width=160,
                                command=self.add_entry, fg_color="#4CAF50", hover_color="#45a049")
        add_btn.pack(pady=8)

        # Clear list button
        clear_btn = ctk.CTkButton(left, text="Clear List", width=160,
                                  command=self.clear_list, fg_color="#FF9800", hover_color="#F57C00")
        clear_btn.pack(pady=4)

        # Confirm/Save button
        confirm_btn = ctk.CTkButton(left, text="Confirm & Save Day", width=160,
                                    command=self.confirm_day, fg_color="#2196F3", hover_color="#1976D2")
        confirm_btn.pack(pady=12)

        # Results / today's list
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, pady=10)

        summary_label = ctk.CTkLabel(right, text="Today's Entries:", anchor="w", font=("Arial", 14, "bold"))
        summary_label.pack(anchor="w", pady=(0, 6))

        self.result = ctk.CTkTextbox(right, width=500, height=320)
        self.result.pack(pady=8, fill="both", expand=True)

    def load_devices(self):
        cursor.execute("SELECT name FROM devices")
        return [row[0] for row in cursor.fetchall()]

    def add_entry(self):
        """Add a device entry to the daily list"""
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

        # Convert to total minutes and calculate kWh/cost
        total_minutes = (hours_val * 60) + minutes_val
        hours = total_minutes / 60
        kwh = (watt * hours) / 1000
        rate = self.current_rate or get_current_rate()
        cost = kwh * rate

        # Store entry
        entry = {
            "device_name": device_name,
            "watt": watt,
            "hours": hours_val,
            "minutes": minutes_val,
            "total_minutes": total_minutes,
            "kwh": kwh,
            "cost": cost,
            "rate": rate
        }
        self.daily_entries.append(entry)

        # Clear input fields
        self.device_var.set("")
        self.entry_hours.delete(0, "end")
        self.entry_minutes.delete(0, "end")

        # Refresh the display
        self.refresh_display()
        messagebox.showinfo("Added", f"{device_name} added to today's list.")

    def refresh_display(self):
        """Update the summary display"""
        self.result.delete("1.0", "end")
        
        if not self.daily_entries:
            self.result.insert("end", "No entries yet. Add devices above.\n")
            return

        total_kwh = 0
        total_cost = 0

        for i, entry in enumerate(self.daily_entries, 1):
            self.result.insert("end", f"{i}. {entry['device_name']}\n")
            self.result.insert("end", f"   Wattage: {entry['watt']}W\n")
            self.result.insert("end", f"   Duration: {entry['hours']:.0f}h {entry['minutes']:.0f}min\n")
            self.result.insert("end", f"   kWh: {entry['kwh']:.4f}\n")
            self.result.insert("end", f"   Cost: ₱{entry['cost']:.2f}\n")
            self.result.insert("end", "\n")
            total_kwh += entry['kwh']
            total_cost += entry['cost']

        # Summary footer
        self.result.insert("end", "─" * 40 + "\n")
        self.result.insert("end", f"Total kWh: {total_kwh:.4f}\n")
        self.result.insert("end", f"Total Cost: ₱{total_cost:.2f}\n")
        self.result.insert("end", f"Rate: ₱{self.current_rate:.2f} / kWh\n")

    def clear_list(self):
        """Clear all entries for the day"""
        if not self.daily_entries:
            messagebox.showinfo("Info", "List is already empty.")
            return
        
        result = messagebox.askyesno("Clear List", "Clear all entries for today?")
        if result:
            self.daily_entries = []
            self.refresh_display()
            messagebox.showinfo("Cleared", "List cleared.")

    def confirm_day(self):
        """Save all entries for the day as a single record"""
        if not self.daily_entries:
            return messagebox.showerror("Error", "Please add at least one device before confirming.")

        try:
            # Create a single record for the day
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = self.controller.current_user_id
            
            # Calculate totals
            total_kwh = sum(entry['kwh'] for entry in self.daily_entries)
            total_cost = sum(entry['cost'] for entry in self.daily_entries)

            # Insert record
            cursor.execute(
                "INSERT INTO records (date, total_kwh, total_cost, user_id) VALUES (?, ?, ?, ?)",
                (today, total_kwh, total_cost, user_id)
            )
            record_id = cursor.lastrowid

            # Insert all entries as record_items
            for entry in self.daily_entries:
                cursor.execute(
                    "INSERT INTO record_items (record_id, device_name, watt_per_hour, duration_minutes, kwh_used, cost) VALUES (?, ?, ?, ?, ?, ?)",
                    (record_id, entry['device_name'], entry['watt'], entry['total_minutes'], entry['kwh'], entry['cost'])
                )

            conn.commit()
            messagebox.showinfo("Saved", f"Day's usage saved! Total: ₱{total_cost:.2f}")
            
            # Clear the list
            self.daily_entries = []
            self.refresh_display()

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("DB Error", f"Failed to save record: {e}")

    def show_menu(self):
        """Show sidebar menu."""
        if self.sidebar is None or not self.sidebar.winfo_exists():
            self.sidebar = Sidebar(self, self.controller, on_close=lambda: setattr(self, 'sidebar', None))

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
            self.refresh_display()
        except Exception:
            pass

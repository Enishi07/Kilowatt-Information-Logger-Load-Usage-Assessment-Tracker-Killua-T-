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

        recent_title = ctk.CTkLabel(right_col, text="Recent Entries (Last 5):",
                                    text_color="#c62828", font=("Arial", 12, "bold"))
        recent_title.pack(pady=(10, 6))

        # Create a frame for the table
        table_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, anchor="w")

        # Table headers
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(header_frame, text="Device", font=("Arial", 11, "bold"), width=100, anchor="w").pack(side="left", padx=(0, 20))
        ctk.CTkLabel(header_frame, text="Duration (h)", font=("Arial", 11, "bold"), width=80, anchor="w").pack(side="left", padx=(0, 20))
        ctk.CTkLabel(header_frame, text="kWh", font=("Arial", 11, "bold"), width=60, anchor="w").pack(side="left", padx=(0, 20))
        ctk.CTkLabel(header_frame, text="Cost (₱)", font=("Arial", 11, "bold"), width=70, anchor="w").pack(side="left")

        # Container for rows
        self.recent_entries_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        self.recent_entries_frame.pack(fill="both", expand=True)

    def on_show(self):
        # Update displayed username when page is shown
        # (image loading is handled by main.show_frame, so don't load images here)
        try:
            uname = getattr(self.controller, 'current_username', None)
            # update textual user label
            if uname:
                self.user_label.configure(text=f"User: {uname}")
            else:
                self.user_label.configure(text="Not logged in")
        except Exception:
            pass
        
        # Load recent entries for current user
        self.load_recent_entries()

    def load_recent_entries(self):
        """Load and display the 5 most recent entries for the current user."""
        # Clear existing rows
        for widget in self.recent_entries_frame.winfo_children():
            widget.destroy()

        try:
            uid = getattr(self.controller, 'current_user_id', None)
            if not uid:
                # No user logged in
                no_data_label = ctk.CTkLabel(
                    self.recent_entries_frame, 
                    text="No user logged in", 
                    font=("Arial", 11),
                    text_color="gray"
                )
                no_data_label.pack(pady=10)
                return

            # Query the 5 most recent record items for this user
            cursor = _db.cursor
            cursor.execute("""
                SELECT ri.device_name, 
                       ri.duration_minutes, 
                       ri.kwh_used, 
                       ri.cost,
                       r.date
                FROM record_items ri
                JOIN records r ON ri.record_id = r.id
                WHERE r.user_id = ?
                ORDER BY r.date DESC, ri.id DESC
                LIMIT 5
            """, (uid,))
            
            rows = cursor.fetchall()
            
            if not rows:
                # No entries found
                no_data_label = ctk.CTkLabel(
                    self.recent_entries_frame, 
                    text="No entries yet", 
                    font=("Arial", 11),
                    text_color="gray"
                )
                no_data_label.pack(pady=10)
                return

            # Display each row
            for device_name, duration_minutes, kwh_used, cost, date in rows:
                row_frame = ctk.CTkFrame(self.recent_entries_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=4)

                # Convert duration to hours
                duration_hours = duration_minutes / 60 if duration_minutes else 0

                # Device name
                device_label = ctk.CTkLabel(
                    row_frame, 
                    text=device_name[:20], 
                    font=("Arial", 10),
                    width=100,
                    anchor="w"
                )
                device_label.pack(side="left", padx=(0, 20))

                # Duration (hours)
                duration_label = ctk.CTkLabel(
                    row_frame, 
                    text=f"{duration_hours:.2f}", 
                    font=("Arial", 10),
                    width=80,
                    anchor="w"
                )
                duration_label.pack(side="left", padx=(0, 20))

                # kWh used
                kwh_label = ctk.CTkLabel(
                    row_frame, 
                    text=f"{kwh_used:.2f}" if kwh_used else "0.00", 
                    font=("Arial", 10),
                    width=60,
                    anchor="w"
                )
                kwh_label.pack(side="left", padx=(0, 20))

                # Cost
                cost_label = ctk.CTkLabel(
                    row_frame, 
                    text=f"₱{cost:.2f}" if cost else "₱0.00", 
                    font=("Arial", 10),
                    width=70,
                    anchor="w"
                )
                cost_label.pack(side="left")

        except Exception as e:
            print(f"[HomePage] Error loading recent entries: {e}")
            error_label = ctk.CTkLabel(
                self.recent_entries_frame, 
                text=f"Error loading entries", 
                font=("Arial", 11),
                text_color="red"
            )
            error_label.pack(pady=10)

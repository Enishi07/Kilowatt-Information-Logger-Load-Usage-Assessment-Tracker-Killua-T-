import customtkinter as ctk
from database import db as _db
from database.db import get_current_rate
from .assets import get_logo


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top bar with title
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        # Title with logo on the left
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=6)
        logo_img = get_logo((36, 36))
        if logo_img:
            logo_lbl = ctk.CTkLabel(title_frame, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))
        title = ctk.CTkLabel(title_frame, text="Killua-T", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Username and profile pic on the right
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 16, "bold"))
        self.user_label.pack(side="right", padx=10)

        # Profile picture placeholder will be updated in on_show
        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
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

        self.rate_label = ctk.CTkLabel(
            right_col,
            text="Current MERALCO Rate: -- PHP / kWh",
            font=("Arial", 16),
        )
        self.rate_label.pack(pady=(30, 10))

        recent_title = ctk.CTkLabel(
            right_col,
            text="Recent Entries:",
            text_color="#c62828",
            font=("Arial", 14, "bold"),
        )
        recent_title.pack(pady=(10, 6))

        # Create a frame for the table
        table_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        table_frame.pack(fill="x", expand=False, anchor="w")

        # Table headers using grid for alignment
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 6))
        for i in range(4):
            header_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(header_frame, text="Device", font=("Arial", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 12))
        ctk.CTkLabel(header_frame, text="Duration (h)", font=("Arial", 13, "bold"), anchor="w").grid(row=0, column=1, sticky="w", padx=(0, 12))
        ctk.CTkLabel(header_frame, text="kWh", font=("Arial", 13, "bold"), anchor="w").grid(row=0, column=2, sticky="w", padx=(0, 12))
        ctk.CTkLabel(header_frame, text="Cost (₱)", font=("Arial", 13, "bold"), anchor="w").grid(row=0, column=3, sticky="w")

        # Container for rows (grid layout)
        self.recent_entries_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        self.recent_entries_frame.pack(fill="x", expand=False)
        for i in range(4):
            self.recent_entries_frame.grid_columnconfigure(i, weight=1)

    def on_show(self):
        # Update displayed username when page is shown
        # (image loading is handled by main.show_frame, so don't load images here)
        try:
            uname = getattr(self.controller, 'current_username', None)
            # update textual user label
            if uname:
                self.user_label.configure(text=uname)
            else:
                self.user_label.configure(text="Not logged in")
            current_rate = get_current_rate()
            self.rate_label.configure(text=f"Current MERALCO Rate: {current_rate:.2f} PHP / kWh")
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
                    font=("Arial", 13),
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
                    font=("Arial", 13),
                    text_color="gray"
                )
                no_data_label.pack(pady=10)
                return

            # Display each row using grid with separators
            for idx, (device_name, duration_minutes, kwh_used, cost, date) in enumerate(rows):
                base_row = idx * 2
                duration_hours = duration_minutes / 60 if duration_minutes else 0

                ctk.CTkLabel(
                    self.recent_entries_frame,
                    text=device_name[:22],
                    font=("Arial", 12),
                    anchor="w"
                ).grid(row=base_row, column=0, sticky="w", padx=(0, 12), pady=3)

                ctk.CTkLabel(
                    self.recent_entries_frame,
                    text=f"{duration_hours:.2f}",
                    font=("Arial", 12),
                    anchor="w"
                ).grid(row=base_row, column=1, sticky="w", padx=(0, 12), pady=3)

                ctk.CTkLabel(
                    self.recent_entries_frame,
                    text=f"{kwh_used:.2f}" if kwh_used else "0.00",
                    font=("Arial", 12),
                    anchor="w"
                ).grid(row=base_row, column=2, sticky="w", padx=(0, 12), pady=3)

                ctk.CTkLabel(
                    self.recent_entries_frame,
                    text=f"₱{cost:.2f}" if cost else "₱0.00",
                    font=("Arial", 12),
                    anchor="w"
                ).grid(row=base_row, column=3, sticky="w", pady=3)

                # Separator line beneath each row
                sep = ctk.CTkFrame(self.recent_entries_frame, height=1, fg_color="#3a3a3a")
                sep.grid(row=base_row + 1, column=0, columnspan=4, sticky="we", pady=(0, 2))

        except Exception as e:
            print(f"[HomePage] Error loading recent entries: {e}")
            error_label = ctk.CTkLabel(
                self.recent_entries_frame, 
                text=f"Error loading entries", 
                font=("Arial", 13),
                text_color="red"
            )
            error_label.pack(pady=10)

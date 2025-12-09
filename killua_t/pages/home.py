import customtkinter as ctk
from database import db as _db


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Top bar with menu and title
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30)
        menu_btn.pack(side="left", padx=10)

        title = ctk.CTkLabel(top, text="Killua-T", font=("Arial", 20, "bold"))
        title.pack(side="top")

        # Show current DB backend (SQLite or MySQL)
        try:
            db_type = getattr(_db, 'DB_TYPE', 'sqlite')
        except Exception:
            db_type = 'sqlite'
        db_label = ctk.CTkLabel(top, text=f"DB: {db_type}", font=("Arial", 10))
        db_label.pack(side="right", padx=10)

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

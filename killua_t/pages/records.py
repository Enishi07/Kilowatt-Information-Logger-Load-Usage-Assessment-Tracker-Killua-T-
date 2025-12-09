import customtkinter as ctk
from database.db import cursor
from .assets import get_logo


class RecordsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Top bar
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
        title = ctk.CTkLabel(title_frame, text="Usage Records", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # add profile pic placeholder on right
        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
        self.profile_pic_lbl.pack(side="right", padx=10)

        back_btn = ctk.CTkButton(top, text="Back", width=80,
                                 command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(side="right", padx=12)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=10)

        self.text = ctk.CTkTextbox(body, width=720, height=420)
        self.text.pack(pady=8)

        self.refresh_records()

    def on_show(self):
        # Refresh records when the page becomes visible
        try:
            self.refresh_records()
        except Exception:
            pass

    def refresh_records(self):
        # Show records for current user only
        user_id = self.controller.current_user_id
        if user_id:
            cursor.execute("SELECT id, date, total_kwh, total_cost FROM records WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT id, date, total_kwh, total_cost FROM records WHERE user_id IS NULL")
        rows = cursor.fetchall()

        self.text.delete("1.0", "end")
        for rec in rows:
            self.text.insert("end", f"Record ID: {rec[0]}\n")
            self.text.insert("end", f"Date: {rec[1]}\n")
            self.text.insert("end", f"Total kWh: {rec[2]}\n")
            self.text.insert("end", f"Total Cost: ₱{rec[3]}\n")
            self.text.insert("end", "------------------------\n")

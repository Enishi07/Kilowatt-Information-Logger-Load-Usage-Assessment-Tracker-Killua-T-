import customtkinter as ctk
from database.db import cursor


class RecordsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="Usage Records", font=("Arial", 25, "bold"))
        title.pack(pady=20)

        back_btn = ctk.CTkButton(self, text="Back to Menu",
                                 command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(pady=10)

        self.text = ctk.CTkTextbox(self, width=700, height=400)
        self.text.pack(pady=20)

        self.refresh_records()

    def refresh_records(self):
        cursor.execute("SELECT id, date, total_kwh, total_cost FROM records")
        rows = cursor.fetchall()

        self.text.delete("1.0", "end")
        for rec in rows:
            self.text.insert("end", f"Record ID: {rec[0]}\n")
            self.text.insert("end", f"Date: {rec[1]}\n")
            self.text.insert("end", f"Total kWh: {rec[2]}\n")
            self.text.insert("end", f"Total Cost: ₱{rec[3]}\n")
            self.text.insert("end", "------------------------\n")

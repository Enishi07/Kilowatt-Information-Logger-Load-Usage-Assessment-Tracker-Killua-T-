import customtkinter as ctk


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="⚡ Killua-T Electricity Tracker",
                             font=("Arial", 30, "bold"))
        title.pack(pady=40)

        sub = ctk.CTkLabel(self, text="Monitor your daily energy usage with ease.",
                           font=("Arial", 16))
        sub.pack()

        # Navigation Buttons
        btn_devices = ctk.CTkButton(self, text="Manage Devices",
                                    command=lambda: controller.show_frame("DevicesPage"))
        btn_devices.pack(pady=20)

        btn_usage = ctk.CTkButton(self, text="Daily Usage Calculator",
                                  command=lambda: controller.show_frame("UsagePage"))
        btn_usage.pack(pady=20)

        btn_records = ctk.CTkButton(self, text="View Records",
                                    command=lambda: controller.show_frame("RecordsPage"))
        btn_records.pack(pady=20)

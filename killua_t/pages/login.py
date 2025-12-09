import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Full page background color similar to screenshot (dark)
        self.configure(fg_color="#141414")

        # Main content: left image area + right rounded form
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=40, pady=40)

        # Left: artwork area (large)
        left = ctk.CTkFrame(content, width=420, height=420, fg_color="transparent")
        left.pack(side="left", padx=(40, 60), pady=10)
        left.pack_propagate(False)

        # Try to load an asset `assets/killua.png` if present, otherwise show placeholder
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        # accept png or jpg uploaded by user
        img_path = os.path.normpath(os.path.join(assets_dir, "killua.png"))
        if not os.path.exists(img_path):
            img_path = os.path.normpath(os.path.join(assets_dir, "killua.jpg"))
        if os.path.exists(img_path):
            try:
                pil = Image.open(img_path).resize((420, 420))
                img = CTkImage(pil, size=(420, 420))
                img_label = ctk.CTkLabel(left, image=img, text="")
                img_label.image = img
                img_label.pack(fill="both", expand=True)
            except Exception:
                placeholder = ctk.CTkLabel(left, text="", fg_color="#0f1720")
                placeholder.pack(fill="both", expand=True)
        else:
            placeholder = ctk.CTkLabel(left, text="", fg_color="#0f1720")
            placeholder.pack(fill="both", expand=True)

        # Right: rounded darker card with inputs
        right = ctk.CTkFrame(content, width=360, height=300, corner_radius=8, fg_color="#5b5b5b")
        right.pack(side="left", pady=10)
        right.pack_propagate(False)

        # Spacing
        spacer = ctk.CTkFrame(right, height=8, fg_color="transparent")
        spacer.pack()

        lbl_user = ctk.CTkLabel(right, text="Username", anchor="w", font=("Arial", 12), text_color="#eaeaea")
        lbl_user.pack(padx=22, pady=(6, 4), fill="x")
        self.entry_user = ctk.CTkEntry(right, placeholder_text="", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_user.pack(padx=22, fill="x")

        lbl_pass = ctk.CTkLabel(right, text="Password", anchor="w", font=("Arial", 12), text_color="#eaeaea")
        lbl_pass.pack(padx=22, pady=(12, 4), fill="x")
        self.entry_pass = ctk.CTkEntry(right, placeholder_text="", show="*", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_pass.pack(padx=22, fill="x")

        # Register button (dark rounded)
        register_btn = ctk.CTkButton(right, text="Register", fg_color="#222222", hover_color="#2e2e2e", width=300, corner_radius=8, command=self.register)
        register_btn.pack(padx=22, pady=18)

        # small hint text under form
        hint = ctk.CTkLabel(right, text="Create an account to start tracking your usage.", font=("Arial", 10), text_color="#d0d0d0")
        hint.pack(padx=22, pady=(0, 12))

    def register(self):
        # For now just navigate to HomePage (placeholder for real auth)
        self.controller.show_frame("HomePage")

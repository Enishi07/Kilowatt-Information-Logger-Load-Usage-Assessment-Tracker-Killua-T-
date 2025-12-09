import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
from tkinter import messagebox
from database.db import conn, cursor
import hashlib


class RegistrationPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#191919")

        # make the content background match the app background
        content = ctk.CTkFrame(self, fg_color="#191919")
        content.pack(expand=True, fill="both", padx=40, pady=40)

        left = ctk.CTkFrame(content, width=420, height=420, fg_color="#191919")
        left.pack(side="left", padx=(40, 60), pady=10)
        left.pack_propagate(False)

        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
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
                placeholder = ctk.CTkLabel(left, text="", fg_color="#191919")
                placeholder.pack(fill="both", expand=True)
        else:
            placeholder = ctk.CTkLabel(left, text="", fg_color="#191919")
            placeholder.pack(fill="both", expand=True)

        right = ctk.CTkFrame(content, width=360, height=360, corner_radius=8, fg_color="#5b5b5b")
        right.pack(side="left", pady=10)
        right.pack_propagate(False)

        lbl_user = ctk.CTkLabel(right, text="Username", anchor="w", font=("Arial", 12), text_color="#eaeaea")
        lbl_user.pack(padx=22, pady=(16, 4), fill="x")
        self.entry_user = ctk.CTkEntry(right, placeholder_text="", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_user.pack(padx=22, fill="x")

        lbl_pass = ctk.CTkLabel(right, text="Password", anchor="w", font=("Arial", 12), text_color="#eaeaea")
        lbl_pass.pack(padx=22, pady=(12, 4), fill="x")
        self.entry_pass = ctk.CTkEntry(right, placeholder_text="", show="*", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_pass.pack(padx=22, fill="x")

        lbl_pass2 = ctk.CTkLabel(right, text="Confirm Password", anchor="w", font=("Arial", 12), text_color="#eaeaea")
        lbl_pass2.pack(padx=22, pady=(12, 4), fill="x")
        self.entry_pass2 = ctk.CTkEntry(right, placeholder_text="", show="*", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_pass2.pack(padx=22, fill="x")

        reg_btn = ctk.CTkButton(right, text="Create Account", width=300, corner_radius=8, command=self.register)
        reg_btn.pack(padx=22, pady=18)

        back = ctk.CTkButton(right, text="Back to Login", width=200, command=lambda: controller.show_frame("LoginPage"))
        back.pack(padx=22)

    def register(self):
        username = self.entry_user.get().strip()
        pw = self.entry_pass.get()
        pw2 = self.entry_pass2.get()

        if not username or not pw:
            return messagebox.showerror("Error", "Please fill all fields.")
        if pw != pw2:
            return messagebox.showerror("Error", "Passwords do not match.")

        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
            conn.commit()
            user_id = cursor.lastrowid
            # set current user in controller
            self.controller.current_user_id = user_id
            self.controller.current_username = username
            messagebox.showinfo("Success", "Account created and logged in.")
            self.controller.show_frame("HomePage")
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("DB Error", f"Failed to create account: {e}")

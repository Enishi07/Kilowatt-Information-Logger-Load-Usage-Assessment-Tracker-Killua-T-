import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Full page background color similar to screenshot (dark)
        self.configure(fg_color="#191919")

        # Main content: left image area + right rounded form
        # make the content background match the app background
        content = ctk.CTkFrame(self, fg_color="#191919")
        content.pack(expand=True, fill="both", padx=40, pady=40)

        # Left: artwork area (large)
        left = ctk.CTkFrame(content, width=420, height=420, fg_color="#191919")
        left.pack(side="left", padx=(40, 60), pady=10)
        left.pack_propagate(False)

        # Prefer the JPG for login screen art; fall back to PNG if missing
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        img_path = os.path.normpath(os.path.join(assets_dir, "killua.jpg"))
        if not os.path.exists(img_path):
            img_path = os.path.normpath(os.path.join(assets_dir, "killua.png"))
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

        # Right: rounded darker card with inputs
        right = ctk.CTkFrame(content, width=360, height=300, corner_radius=8, fg_color="#5b5b5b")
        right.pack(side="left", pady=10)
        right.pack_propagate(False)

        # Spacing
        spacer = ctk.CTkFrame(right, height=8, fg_color="transparent")
        spacer.pack()

        lbl_user = ctk.CTkLabel(right, text="Username", anchor="w", font=("Arial", 14), text_color="#eaeaea")
        lbl_user.pack(padx=22, pady=(6, 4), fill="x")
        self.entry_user = ctk.CTkEntry(right, placeholder_text="", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_user.pack(padx=22, fill="x")

        lbl_pass = ctk.CTkLabel(right, text="Password", anchor="w", font=("Arial", 14), text_color="#eaeaea")
        lbl_pass.pack(padx=22, pady=(12, 4), fill="x")
        self.entry_pass = ctk.CTkEntry(right, placeholder_text="", show="*", width=300, fg_color="#ffffff", text_color="#000")
        self.entry_pass.pack(padx=22, fill="x")

        # Login button
        login_btn = ctk.CTkButton(right, text="Login", fg_color="#222222", hover_color="#2e2e2e", width=300, corner_radius=8, command=self.login, font=("Arial", 13, "bold"))
        login_btn.pack(padx=22, pady=12)

        # Clickable signup hint
        signup = ctk.CTkLabel(right, text="Don't have an account? Sign up here.", font=("Arial", 12), text_color="#d0d0d0")
        signup.pack(padx=22, pady=(6, 12))
        # Make the label clickable by binding to click event
        signup.bind("<Button-1>", lambda e: self.controller.show_frame("RegistrationPage"))

    def login(self):
        username = self.entry_user.get().strip()
        pw = self.entry_pass.get()
        
        # Data validation for missing fields
        if not username and not pw:
            from tkinter import messagebox
            messagebox.showerror("Validation Error", "Please enter both Username and Password.")
            return
        elif not username:
            from tkinter import messagebox
            messagebox.showerror("Validation Error", "Please enter your Username.")
            return
        elif not pw:
            from tkinter import messagebox
            messagebox.showerror("Validation Error", "Please enter your Password.")
            return

        import hashlib
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        try:
            cursor = __import__('database.db', fromlist=['cursor']).cursor
            cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
            row = cursor.fetchone()
            if row:
                user_id = row[0]
                self.controller.current_user_id = user_id
                self.controller.current_username = username
                self.controller.show_frame("HomePage")
            else:
                from tkinter import messagebox
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Login error: {e}")

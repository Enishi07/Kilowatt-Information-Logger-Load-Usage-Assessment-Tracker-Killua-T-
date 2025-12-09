import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
from tkinter import filedialog, messagebox
from database.db import conn, cursor
from .assets import load_image


class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(fg_color="#191919")

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        title = ctk.CTkLabel(top, text="Profile", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=10)

        back_btn = ctk.CTkButton(top, text="Back", width=80, command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(side="right", padx=12)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=10)

        left = ctk.CTkFrame(body, width=300, fg_color="transparent")
        left.pack(side="left", padx=(10, 30), pady=10)

        # Profile picture area
        self.img_label = ctk.CTkLabel(left, text="", width=200, height=200)
        self.img_label.pack(pady=8)

        upload_btn = ctk.CTkButton(left, text="Upload Picture", command=self.upload_picture)
        upload_btn.pack(pady=8)

        # Short bio / description
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, pady=10)

        lbl = ctk.CTkLabel(right, text="Short Description:", anchor="w")
        lbl.pack(anchor="w")
        self.bio_entry = ctk.CTkTextbox(right, width=420, height=120)
        self.bio_entry.pack(pady=8)

        save_btn = ctk.CTkButton(right, text="Save Profile", width=160, command=self.save_profile)
        save_btn.pack(pady=6)

        # Stats area
        stats_title = ctk.CTkLabel(right, text="Statistics:", font=("Arial", 12, "bold"))
        stats_title.pack(pady=(18, 6), anchor="w")

        self.stats_label = ctk.CTkLabel(right, text="- Total kWh: 0\n- Most used device: -", justify="left")
        self.stats_label.pack(anchor="w")

        self.refresh()

    def on_show(self):
        self.refresh()

    def refresh(self):
        uid = getattr(self.controller, 'current_user_id', None)
        print(f"[ProfilePage.refresh] uid={uid}")
        if not uid:
            # clear any previous image
            try:
                self.img_label.configure(image=None, text="Not logged in")
            except Exception:
                try:
                    self.img_label.configure(text="Not logged in")
                except Exception:
                    pass
            try:
                if hasattr(self.img_label, 'image'):
                    del self.img_label.image
            except Exception:
                pass
            self.bio_entry.delete("1.0", "end")
            self.stats_label.configure(text="- Total kWh: 0\n- Most used device: -")
            return

        # Load profile pic from users.profile_pic
        cursor.execute("SELECT profile_pic, bio FROM users WHERE id = ?", (uid,))
        row = cursor.fetchone()
        img_path = None
        bio = ""
        if row:
            img_path = row[0]
            bio = row[1] or ""
        print(f"[ProfilePage.refresh] img_path from DB = {repr(img_path)}")

        # load and show image
        img = None
        if img_path:
            img = load_image(img_path, size=(180, 180), circle=True)
            print(f"[ProfilePage.refresh] loaded image: {img is not None}")
        if img:
            print(f"[ProfilePage.refresh] setting img_label to image")
            self.img_label.configure(image=img, text="")
            self.img_label.image = img
        else:
            print(f"[ProfilePage.refresh] clearing img_label (no image)")
            # clear any previous image and show placeholder text
            try:
                self.img_label.configure(image=None, text="No Image")
            except Exception:
                try:
                    self.img_label.configure(text="No Image")
                except Exception:
                    pass
            try:
                if hasattr(self.img_label, 'image'):
                    del self.img_label.image
            except Exception:
                pass

        self.bio_entry.delete("1.0", "end")
        self.bio_entry.insert("end", bio)

        # compute stats: total kwh and most used device
        cursor.execute("SELECT SUM(total_kwh) FROM records WHERE user_id = ?", (uid,))
        total = cursor.fetchone()[0] or 0.0

        cursor.execute("""
        SELECT ri.device_name, SUM(ri.duration_minutes) as total_minutes, SUM(ri.kwh_used) as total_kwh
        FROM record_items ri
        JOIN records r ON ri.record_id = r.id
        WHERE r.user_id = ?
        GROUP BY ri.device_name
        ORDER BY total_minutes DESC
        LIMIT 1
        """, (uid,))
        row2 = cursor.fetchone()
        if row2:
            device, total_minutes, dev_kwh = row2[0], row2[1] or 0.0, row2[2] or 0.0
            stats_text = f"- Total kWh: {total:.4f}\n- Most used device: {device} ({total_minutes:.1f} min), {dev_kwh:.4f} kWh"
        else:
            stats_text = f"- Total kWh: {total:.4f}\n- Most used device: -"

        self.stats_label.configure(text=stats_text)

    def upload_picture(self):
        uid = getattr(self.controller, 'current_user_id', None)
        if not uid:
            return messagebox.showerror("Error", "Login to upload a profile picture.")
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not path:
            return
        # copy to assets/profiles/<uid>.<ext>
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        profiles_dir = os.path.join(assets_dir, "profiles")
        os.makedirs(profiles_dir, exist_ok=True)
        ext = os.path.splitext(path)[1].lower()
        dest = os.path.join(profiles_dir, f"{uid}{ext}")
        try:
            # Get the old profile_pic path from DB to delete the old file later
            cursor.execute("SELECT profile_pic FROM users WHERE id = ?", (uid,))
            row = cursor.fetchone()
            old_profile_pic = row[0] if row else None
            
            # Write new file
            with open(path, 'rb') as rf, open(dest, 'wb') as wf:
                wf.write(rf.read())
            # update DB with relative path
            rel = os.path.relpath(dest, os.path.join(os.path.dirname(__file__), "..", "assets"))
            cursor.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (rel, uid))
            conn.commit()
            
            # Delete old profile picture file if it exists and is different
            if old_profile_pic and old_profile_pic != rel:
                try:
                    old_full = os.path.normpath(os.path.join(assets_dir, old_profile_pic))
                    if os.path.exists(old_full):
                        os.remove(old_full)
                except Exception:
                    pass
            
            # Clear the image cache so the new image loads fresh
            from .assets import clear_image_cache
            clear_image_cache(rel)
            if old_profile_pic:
                clear_image_cache(old_profile_pic)
            
            messagebox.showinfo("Saved", "Profile picture uploaded.")
            # refresh this page and propagate the new image to other frames
            self.refresh()
            try:
                self.controller.show_frame("ProfilePage")
            except Exception:
                pass
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("Error", f"Failed to upload: {e}")

    def save_profile(self):
        uid = getattr(self.controller, 'current_user_id', None)
        if not uid:
            return messagebox.showerror("Error", "Login first.")
        bio = self.bio_entry.get("1.0", "end").strip()
        try:
            cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, uid))
            conn.commit()
            messagebox.showinfo("Saved", "Profile updated.")
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("Error", f"Failed to save profile: {e}")

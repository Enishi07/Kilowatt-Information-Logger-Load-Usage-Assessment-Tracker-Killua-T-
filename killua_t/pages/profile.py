import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
from tkinter import filedialog, messagebox
from database.db import conn, cursor
from .assets import load_image, get_logo
from .sidebar import Sidebar
from datetime import datetime


class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sidebar = None
        self.configure(fg_color="#191919")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        # Left cluster: menu, logo, title
        left_cluster = ctk.CTkFrame(top, fg_color="transparent")
        left_cluster.pack(side="left", padx=6)

        self.menu_btn = ctk.CTkButton(left_cluster, text="☰", font=("Arial", 16), width=40, command=self.show_menu)
        self.menu_btn.pack(side="left", padx=(0, 10))

        logo_img = get_logo((36, 36))
        if logo_img:
            logo_lbl = ctk.CTkLabel(left_cluster, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(left_cluster, text="Profile", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Username label on right
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 16, "bold"))
        self.user_label.pack(side="right", padx=10)

        # Profile picture label on right (will be filled by main.show_frame)
        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=32, height=32)
        self.profile_pic_lbl.pack(side="right", padx=8)

        # Scrollable body
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=10)

        left = ctk.CTkFrame(body, width=300, fg_color="transparent")
        left.pack(side="left", padx=(10, 30), pady=10)

        # Username label above profile picture
        self.username_label = ctk.CTkLabel(left, text="", font=("Arial", 16, "bold"))
        self.username_label.pack(pady=(0, 8))

        # Profile picture area
        self.img_label = ctk.CTkLabel(left, text="", width=200, height=200)
        self.img_label.pack(pady=8)

        upload_btn = ctk.CTkButton(left, text="Upload Picture", command=self.upload_picture)
        upload_btn.pack(pady=8)

        # Short bio / description
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, pady=10)

        # Bio display label (always visible)
        self.bio_display = ctk.CTkLabel(right, text="", justify="left", anchor="w", wraplength=400, font=("Arial", 13))
        self.bio_display.pack(anchor="w", pady=(0, 8))

        # Edit bio button
        edit_bio_btn = ctk.CTkButton(right, text="Edit Description", width=160, command=self.toggle_bio_editor, font=("Arial", 13))
        edit_bio_btn.pack(anchor="w", pady=(0, 8))

        # Bio editor (hidden by default)
        self.bio_entry = ctk.CTkTextbox(right, width=420, height=120)

        save_btn = ctk.CTkButton(right, text="Save Profile", width=160, command=self.save_profile, fg_color="#4CAF50", hover_color="#45a049")
        self.save_btn = save_btn

        # Stats area
        stats_title = ctk.CTkLabel(right, text="Statistics:", font=("Arial", 14, "bold"))
        stats_title.pack(pady=(18, 6), anchor="w")

        # Monthly cost
        self.monthly_cost_label = ctk.CTkLabel(right, text="", justify="left", font=("Arial", 13))
        self.monthly_cost_label.pack(anchor="w", pady=(0, 10))

        # Total kWh label
        self.total_kwh_label = ctk.CTkLabel(right, text="- Total kWh: 0", justify="left", font=("Arial", 13))
        self.total_kwh_label.pack(anchor="w", pady=(0, 10))

        # Top devices title
        top_devices_title = ctk.CTkLabel(right, text="Top 5 Most Used Devices:", font=("Arial", 13, "bold"))
        top_devices_title.pack(anchor="w", pady=(10, 6))

        # Scrollable container for device bars
        self.devices_container = ctk.CTkScrollableFrame(right, fg_color="transparent", height=200)
        self.devices_container.pack(fill="both", expand=True, anchor="w")

        self.bio_visible = False

        self.refresh()

    def on_show(self):
        try:
            uname = getattr(self.controller, 'current_username', None)
            if uname:
                self.user_label.configure(text=uname)
            else:
                self.user_label.configure(text="Not logged in")
        except Exception:
            pass
        self.refresh()

    def toggle_bio_editor(self):
        """Toggle the bio textbox visibility."""
        if self.bio_visible:
            self.bio_entry.pack_forget()
            self.save_btn.pack_forget()
            self.bio_visible = False
        else:
            self.bio_entry.pack(pady=8, anchor="w")
            self.save_btn.pack(pady=6, anchor="w")
            self.bio_visible = True

    def refresh(self):
        uid = getattr(self.controller, 'current_user_id', None)
        if not uid:
            self.username_label.configure(text="")
            self.bio_display.configure(text="")
            self.bio_entry.delete("1.0", "end")
            self.total_kwh_label.configure(text="- Total kWh: 0")
            self.monthly_cost_label.configure(text="")
            # Clear device bars
            for widget in self.devices_container.winfo_children():
                widget.destroy()
            return

        # Load username and bio
        cursor.execute("SELECT username, bio FROM users WHERE id = ?", (uid,))
        row = cursor.fetchone()
        username = ""
        bio = ""
        if row:
            username = row[0] or ""
            bio = row[1] or ""

        self.username_label.configure(text=username)
        self.bio_display.configure(text=bio if bio else "No description set.")
        self.bio_entry.delete("1.0", "end")
        self.bio_entry.insert("end", bio)

        # Calculate monthly cost for current month
        current_month = datetime.now().strftime("%Y-%m")
        cursor.execute("""
            SELECT SUM(total_cost) FROM records 
            WHERE user_id = ? AND date LIKE ?
        """, (uid, f"{current_month}%"))
        monthly_cost = cursor.fetchone()[0] or 0.0
        month_name = datetime.now().strftime("%B %Y")
        self.monthly_cost_label.configure(text=f"Total Cost ({month_name}): ₱{monthly_cost:.2f}")

        # Compute total kwh
        cursor.execute("SELECT SUM(total_kwh) FROM records WHERE user_id = ?", (uid,))
        total = cursor.fetchone()[0] or 0.0
        self.total_kwh_label.configure(text=f"- Total kWh: {total:.4f}")

        # Get top 5 most used devices
        cursor.execute("""
        SELECT 
            ri.device_name, 
            SUM(ri.duration_minutes) as total_minutes, 
            SUM(ri.kwh_used) as total_kwh,
            SUM(ri.cost) as total_cost
        FROM record_items ri
        JOIN records r ON ri.record_id = r.id
        WHERE r.user_id = ?
        GROUP BY ri.device_name
        ORDER BY total_minutes DESC
        LIMIT 5
        """, (uid,))
        top_devices = cursor.fetchall()

        # Clear previous bars
        for widget in self.devices_container.winfo_children():
            widget.destroy()

        if not top_devices:
            no_data = ctk.CTkLabel(self.devices_container, text="No device usage data", text_color="gray", font=("Arial", 12))
            no_data.pack(anchor="w", pady=5)
        else:
            # Find max hours for scaling
            max_hours = max([d[1] / 60 for d in top_devices])
            
            for device_name, total_minutes, total_kwh, total_cost in top_devices:
                hours = total_minutes / 60
                self.create_device_bar(device_name, hours, total_kwh or 0.0, total_cost or 0.0, max_hours)

    def create_device_bar(self, device_name, hours, kwh, cost, max_hours):
        """Create a horizontal bar graph for a device."""
        bar_frame = ctk.CTkFrame(self.devices_container, fg_color="transparent")
        bar_frame.pack(fill="x", pady=6, padx=0)

        # Bar visualization
        bar_container = ctk.CTkFrame(bar_frame, fg_color="transparent")
        bar_container.pack(fill="x")

        # Hours label (left side)
        hours_label = ctk.CTkLabel(bar_container, text=f"{hours:.1f}h", font=("Arial", 12), width=50, anchor="e")
        hours_label.pack(side="left", padx=(0, 10))

        # Progress bar
        bar_width = int((hours / max_hours) * 300) if max_hours > 0 else 0
        bar = ctk.CTkProgressBar(bar_container, width=300, height=20)
        bar.pack(side="left")
        bar.set(hours / max_hours if max_hours > 0 else 0)

        # Device info below bar
        info_frame = ctk.CTkFrame(bar_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=(60, 0))

        device_label = ctk.CTkLabel(info_frame, text=device_name, font=("Arial", 11, "bold"), anchor="w")
        device_label.pack(anchor="w")

        details_label = ctk.CTkLabel(info_frame, text=f"{kwh:.2f} kWh • ₱{cost:.2f}", font=("Arial", 10), text_color="gray", anchor="w")
        details_label.pack(anchor="w")

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
            # Hide the editor and update the display
            self.bio_entry.pack_forget()
            self.save_btn.pack_forget()
            self.bio_visible = False
            self.bio_display.configure(text=bio if bio else "No description set.")
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    def on_show(self):
        """Update username label when the page becomes visible."""
        try:
            uname = getattr(self.controller, 'current_username', None)
            if uname:
                self.user_label.configure(text=f"User: {uname}")
            else:
                self.user_label.configure(text="Not logged in")
            self.refresh()
        except Exception as e:
            print(f"[ProfilePage] Error in on_show: {e}")

    def show_menu(self):
        """Show sidebar menu."""
        if self.sidebar is None or not self.sidebar.winfo_exists():
            self.sidebar = Sidebar(self, self.controller, on_close=lambda: setattr(self, 'sidebar', None))

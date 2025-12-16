import customtkinter as ctk
from tkinter import messagebox
from database.db import conn, cursor
from .assets import get_logo
from .sidebar import Sidebar


class DevicesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sidebar = None
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30, command=self.show_menu)
        menu_btn.pack(side="left", padx=10)

        # Title with logo
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=6)
        logo_img = get_logo((36, 36))
        if logo_img:
            logo_lbl = ctk.CTkLabel(title_frame, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))
        title = ctk.CTkLabel(title_frame, text="Add / Manage Devices", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Right side: username and profile pic
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 16, "bold"))
        self.user_label.pack(side="right", padx=10)

        # profile pic placeholder on right
        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
        self.profile_pic_lbl.pack(side="right", padx=6)

        # Body layout
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=10)

        form = ctk.CTkFrame(body, fg_color="transparent")
        form.pack(anchor="n", pady=10)

        label_name = ctk.CTkLabel(form, text="Device Name:", anchor="w", font=("Arial", 14))
        label_name.grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.entry_name = ctk.CTkEntry(form, placeholder_text="Device Name", width=360)
        self.entry_name.grid(row=0, column=1, padx=6, pady=6)

        label_watt = ctk.CTkLabel(form, text="Device Stable Wattage:", anchor="w", font=("Arial", 14))
        label_watt.grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.entry_watt = ctk.CTkEntry(form, placeholder_text="Stable Wattage (W)", width=360)
        self.entry_watt.grid(row=1, column=1, padx=6, pady=6)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=2, column=1, pady=12)

        add_btn = ctk.CTkButton(actions, text="Add Device", width=120, command=self.add_device, fg_color="#4CAF50", hover_color="#45a049")
        add_btn.pack(side="left", padx=8)

        clear_btn = ctk.CTkButton(actions, text="Clear", width=100, command=self.clear_form)
        clear_btn.pack(side="left", padx=8)

        list_label = ctk.CTkLabel(body, text="Device List:", anchor="w", font=("Arial", 14, "bold"))
        list_label.pack(anchor="w", pady=(14, 6))

        # Scrollable frame for device list
        self.device_list_frame = ctk.CTkScrollableFrame(body, width=700, height=240)
        self.device_list_frame.pack(pady=6, fill="both", expand=True)

        self.refresh_devices()

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_watt.delete(0, "end")

    def add_device(self):
        name = self.entry_name.get()
        watt = self.entry_watt.get()

        if not name or not watt:
            return messagebox.showerror("Error", "Please fill all fields.")

        # associate device with current user (if any); allow NULL for shared devices
        user_id = self.controller.current_user_id
        cursor.execute("INSERT INTO devices (name, watt_per_hour, user_id) VALUES (?, ?, ?)",
                   (name, float(watt), user_id))
        conn.commit()

        self.refresh_devices()
        self.clear_form()

    def refresh_devices(self):
        # Clear existing device items
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        # show devices for the current user and shared devices (user_id IS NULL)
        user_id = self.controller.current_user_id
        if user_id:
            cursor.execute("SELECT id, name, watt_per_hour, user_id FROM devices WHERE user_id = ? OR user_id IS NULL", (user_id,))
        else:
            cursor.execute("SELECT id, name, watt_per_hour, user_id FROM devices WHERE user_id IS NULL")
        rows = cursor.fetchall()

        for device_id, name, watt, owner_id in rows:
            # Create a frame for each device
            device_frame = ctk.CTkFrame(self.device_list_frame, fg_color="#2b2b2b")
            device_frame.pack(fill="x", padx=5, pady=2)

            # Device info label
            info_text = f"{name} — {watt} W"
            if owner_id is None:
                info_text += " (Shared)"
            device_label = ctk.CTkLabel(device_frame, text=info_text, anchor="w", font=("Arial", 13))
            device_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            # Show edit/delete buttons for user's own devices and shared devices
            can_modify = (owner_id == user_id) or (owner_id is None)
            
            if can_modify:
                # Edit button
                edit_btn = ctk.CTkButton(
                    device_frame,
                    text="Edit",
                    width=60,
                    height=28,
                    fg_color="#2196F3",
                    hover_color="#1976D2",
                    command=lambda d_id=device_id, d_name=name, d_watt=watt: self.edit_device(d_id, d_name, d_watt)
                )
                edit_btn.pack(side="right", padx=3, pady=5)

                # Delete button (X)
                delete_btn = ctk.CTkButton(
                    device_frame,
                    text="✕",
                    width=40,
                    height=28,
                    fg_color="#f44336",
                    hover_color="#d32f2f",
                    command=lambda d_id=device_id, d_name=name: self.delete_device(d_id, d_name)
                )
                delete_btn.pack(side="right", padx=3, pady=5)

    def edit_device(self, device_id, current_name, current_watt):
        """Edit an existing device"""
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Device")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Content frame
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(content, text="Edit Device", font=("Arial", 18, "bold"))
        title.pack(pady=(0, 20))

        # Device name
        name_label = ctk.CTkLabel(content, text="Device Name:", anchor="w", font=("Arial", 13))
        name_label.pack(anchor="w", pady=(0, 5))
        name_entry = ctk.CTkEntry(content, width=360, height=35)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=(0, 10))

        # Wattage
        watt_label = ctk.CTkLabel(content, text="Device Stable Wattage:", anchor="w", font=("Arial", 13))
        watt_label.pack(anchor="w", pady=(0, 5))
        watt_entry = ctk.CTkEntry(content, width=360, height=35)
        watt_entry.insert(0, str(current_watt))
        watt_entry.pack(pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack()

        def save_changes():
            new_name = name_entry.get()
            new_watt = watt_entry.get()

            if not new_name or not new_watt:
                messagebox.showerror("Error", "Please fill all fields.", parent=dialog)
                return

            try:
                watt_float = float(new_watt)
                cursor.execute("UPDATE devices SET name = ?, watt_per_hour = ? WHERE id = ?",
                              (new_name, watt_float, device_id))
                conn.commit()
                self.refresh_devices()
                dialog.destroy()
                messagebox.showinfo("Success", "Device updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Wattage must be a valid number.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update device: {str(e)}", parent=dialog)

        save_btn = ctk.CTkButton(btn_frame, text="Save", width=120, command=save_changes,
                                 fg_color="#4CAF50", hover_color="#45a049")
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=100, command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)

    def delete_device(self, device_id, device_name):
        """Delete a device after confirmation"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{device_name}'?\n\nThis action cannot be undone."
        )
        
        if result:
            try:
                cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
                conn.commit()
                self.refresh_devices()
                messagebox.showinfo("Success", f"Device '{device_name}' deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete device: {str(e)}")

    def on_show(self):
        # Refresh when the page becomes visible
        # (image loading is handled by main.show_frame, so don't load images here)
        try:
            uname = getattr(self.controller, 'current_username', None)
            if uname:
                self.user_label.configure(text=uname)
            else:
                self.user_label.configure(text="Not logged in")
            self.refresh_devices()
        except Exception:
            pass

    def show_menu(self):
        """Show sidebar menu."""
        if self.sidebar is None or not self.sidebar.winfo_exists():
            self.sidebar = Sidebar(self, self.controller, on_close=lambda: setattr(self, 'sidebar', None))


import customtkinter as ctk


class Sidebar(ctk.CTkToplevel):
    """A sidebar menu that appears when the menu button is clicked."""
    
    def __init__(self, parent, controller, on_close=None):
        super().__init__(parent)
        self.controller = controller
        self.on_close = on_close
        self.parent = parent
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Keep on top
        
        # Set initial position (will update height after window renders)
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()

        menu_width = 250
        self.geometry(f"{menu_width}x500+{parent_x}+{parent_y}")
        self.configure(fg_color="#2b2b2b")

        # Make sure this toplevel is visible and on top before sizing
        self.wait_visibility(self)
        self.lift()
        self.focus_force()

        # Update geometry after window is visible and whenever the window resizes
        self.after(10, self.update_geometry)
        try:
            self.parent.winfo_toplevel().bind("<Configure>", lambda e: self.update_geometry())
        except Exception:
            pass
        
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True)
        
        # Close button at top
        close_btn = ctk.CTkButton(
            main_frame, 
            text="✕", 
            width=40, 
            height=30,
            command=self.close_sidebar,
            fg_color="#2b2b2b",
            hover_color="#3b3b3b",
            font=("Arial", 14)
        )
        close_btn.pack(pady=10)
        
        # Menu items
        menu_items = [
            ("Home", "HomePage"),
            ("Daily Usage", "UsagePage"),
            ("Add / Manage Devices", "DevicesPage"),
            ("View Records", "RecordsPage"),
            ("MERALCO Rate", "MeralcoRatePage"),
            ("Profile", "ProfilePage"),
        ]
        
        for label, page_name in menu_items:
            btn = ctk.CTkButton(
                main_frame,
                text=label,
                width=200,
                height=40,
                fg_color="#1f6aa5",
                hover_color="#2575c7",
                text_color="white",
                font=("Arial", 14),
                command=lambda pn=page_name: self.navigate(pn)
            )
            btn.pack(pady=8, padx=15, fill="x")
        
        # Sidebar stays open until X or navigation is clicked
        
    def navigate(self, page_name):
        """Navigate to a page and close the sidebar."""
        self.controller.show_frame(page_name)
        self.close_sidebar()
    
    def close_sidebar(self):
        """Close the sidebar."""
        if self.on_close:
            self.on_close()
        self.destroy()

    def update_geometry(self):
        """Update sidebar height to match parent window height."""
        try:
            # Prefer the toplevel (controller) height for accuracy
            root = self.parent.winfo_toplevel()
            root.update_idletasks()
            parent_x = root.winfo_rootx()
            parent_y = root.winfo_rooty()
            parent_height = root.winfo_height()

            # Use a fixed proportion of window height to avoid overlap
            top_margin = 10
            height = max(300, int(parent_height * 0.75))

            menu_width = 250
            self.geometry(f"{menu_width}x{height}+{parent_x}+{parent_y + top_margin}")
        except:
            pass


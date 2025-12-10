import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

from .assets import get_logo
from .sidebar import Sidebar
from database.db import get_current_rate, add_meralco_rate, get_rate_history


class MeralcoRatePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sidebar = None
        self.current_rate = get_current_rate()
        self.canvas = None
        self.figure = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        # Left cluster with menu, logo, title
        left_cluster = ctk.CTkFrame(top, fg_color="transparent")
        left_cluster.pack(side="left", padx=6)

        menu_btn = ctk.CTkButton(left_cluster, text="☰", width=40, height=30, command=self.show_menu)
        menu_btn.pack(side="left", padx=(0, 10))

        logo_img = get_logo((36, 36))
        if logo_img:
            logo_lbl = ctk.CTkLabel(left_cluster, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(left_cluster, text="MERALCO Rate", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # Right side: username and profile pic
        self.user_label = ctk.CTkLabel(top, text="", font=("Arial", 16, "bold"))
        self.user_label.pack(side="right", padx=10)

        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
        self.profile_pic_lbl.pack(side="right", padx=6)

        # Body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=10)

        # Left panel: current rate and editor
        left_panel = ctk.CTkFrame(body, fg_color="transparent")
        left_panel.pack(side="left", padx=(0, 30), pady=10, anchor="n")

        self.rate_label = ctk.CTkLabel(left_panel, text="", font=("Arial", 16, "bold"))
        self.rate_label.pack(anchor="w", pady=(0, 10))

        self.last_updated_label = ctk.CTkLabel(left_panel, text="", font=("Arial", 12), text_color="gray")
        self.last_updated_label.pack(anchor="w", pady=(0, 14))

        new_rate_label = ctk.CTkLabel(left_panel, text="Set new rate (PHP / kWh):", font=("Arial", 13))
        new_rate_label.pack(anchor="w", pady=(0, 6))

        self.new_rate_entry = ctk.CTkEntry(left_panel, width=200, placeholder_text="e.g. 12.75")
        self.new_rate_entry.pack(anchor="w", pady=(0, 8))

        update_btn = ctk.CTkButton(left_panel, text="Update Rate", width=160, fg_color="#4CAF50", hover_color="#45a049", command=self.update_rate, font=("Arial", 13, "bold"))
        update_btn.pack(anchor="w", pady=(4, 12))

        self.status_label = ctk.CTkLabel(left_panel, text="", font=("Arial", 12), text_color="gray")
        self.status_label.pack(anchor="w")

        # Right panel: graph
        right_panel = ctk.CTkFrame(body, fg_color="transparent")
        right_panel.pack(side="left", fill="both", expand=True, pady=10)

        self.canvas_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True)

        self.refresh_all()

    def show_menu(self):
        if self.sidebar is None or not self.sidebar.winfo_exists():
            self.sidebar = Sidebar(self, self.controller, on_close=lambda: setattr(self, 'sidebar', None))

    def on_show(self):
        try:
            uname = getattr(self.controller, 'current_username', None)
            self.user_label.configure(text=uname if uname else "Not logged in")
        except Exception:
            pass
        self.refresh_all()

    def refresh_all(self):
        self.current_rate = get_current_rate()
        self.rate_label.configure(text=f"Current Rate: {self.current_rate:.2f} PHP / kWh")
        history = get_rate_history(limit=50)
        if history:
            last_ts = history[-1][0]
            try:
                dt = datetime.fromisoformat(str(last_ts))
                pretty = dt.strftime("%b %d, %Y %H:%M")
            except Exception:
                pretty = str(last_ts)
            self.last_updated_label.configure(text=f"Last updated: {pretty}")
        else:
            self.last_updated_label.configure(text="No history yet")
        self.draw_graph(history)
        self.status_label.configure(text="")

    def update_rate(self):
        raw = self.new_rate_entry.get().strip()
        try:
            new_rate = float(raw)
        except ValueError:
            messagebox.showerror("Invalid", "Please enter a numeric rate (e.g. 12.75).")
            return
        if new_rate <= 0:
            messagebox.showerror("Invalid", "Rate must be greater than 0.")
            return
        try:
            add_meralco_rate(new_rate)
            self.new_rate_entry.delete(0, "end")
            self.status_label.configure(text="Rate updated.", text_color="#4CAF50")
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update rate: {e}")

    def draw_graph(self, history):
        # Clear previous widgets/canvas
        for child in self.canvas_frame.winfo_children():
            child.destroy()
        self.canvas = None
        self.figure = None

        if not history:
            empty = ctk.CTkLabel(self.canvas_frame, text="No rate history yet", text_color="gray", font=("Arial", 14))
            empty.pack(expand=True)
            return

        dates = [h[0] for h in history]
        rates = [float(h[1]) for h in history]

        # Convert dates to display-friendly labels
        labels = []
        for d in dates:
            try:
                labels.append(datetime.fromisoformat(str(d)).strftime("%m-%d"))
            except Exception:
                labels.append(str(d))

        self.figure = Figure(figsize=(5.5, 3.5), dpi=100, facecolor="#212121", edgecolor="white")
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#1a1a1a")

        ax.plot(range(len(rates)), rates, marker='o', linewidth=2, markersize=6, color="#ffa000")
        ax.fill_between(range(len(rates)), rates, alpha=0.25, color="#ffa000")

        ax.set_xlabel("Update", fontsize=12, color="white")
        ax.set_ylabel("Rate (PHP / kWh)", fontsize=12, color="white")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10, color="white")
        ax.tick_params(axis='y', labelcolor='white')
        ax.grid(True, alpha=0.2, color="white")

        for spine in ax.spines.values():
            spine.set_color("white")

        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

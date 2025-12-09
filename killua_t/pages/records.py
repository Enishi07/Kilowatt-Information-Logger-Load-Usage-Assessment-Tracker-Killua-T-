import customtkinter as ctk
from database.db import cursor, conn
from .assets import get_logo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime


class RecordsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=10)

        menu_btn = ctk.CTkButton(top, text="☰", width=40, height=30)
        menu_btn.pack(side="left", padx=10)

        # Title with logo
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=6)
        logo_img = get_logo((28, 28))
        if logo_img:
            logo_lbl = ctk.CTkLabel(title_frame, image=logo_img, text="")
            logo_lbl.image = logo_img
            logo_lbl.pack(side="left", padx=(0, 8))
        title = ctk.CTkLabel(title_frame, text="Usage Records", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # add profile pic placeholder on right
        self.profile_pic_lbl = ctk.CTkLabel(top, text="", width=28, height=28)
        self.profile_pic_lbl.pack(side="right", padx=10)

        back_btn = ctk.CTkButton(top, text="Back", width=80,
                                 command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(side="right", padx=12)

        # Main body with two columns: left (records list) and right (graph)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=30, pady=10)

        # Left column: Records list with scrollbar
        left_col = ctk.CTkFrame(body, fg_color="transparent", width=280)
        left_col.pack(side="left", fill="both", padx=(0, 20))
        left_col.pack_propagate(False)

        left_title = ctk.CTkLabel(left_col, text="Records", font=("Arial", 14, "bold"), text_color="#c62828")
        left_title.pack(pady=(0, 10))

        # Scrollable frame for records
        records_scroll = ctk.CTkScrollableFrame(left_col, fg_color="transparent")
        records_scroll.pack(fill="both", expand=True)
        self.records_container = records_scroll

        # Right column: Graph and refresh button
        right_col = ctk.CTkFrame(body, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        # Canvas for matplotlib figure
        self.canvas_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.canvas = None
        self.figure = None

        # Refresh button below graph
        refresh_btn = ctk.CTkButton(
            right_col, 
            text="Refresh Graph", 
            command=self.refresh_records,
            height=35
        )
        refresh_btn.pack(fill="x", pady=(10, 0))

    def on_show(self):
        # Refresh records when the page becomes visible
        try:
            self.refresh_records()
        except Exception as e:
            print(f"[RecordsPage] Error in on_show: {e}")

    def refresh_records(self):
        """Load records from DB and update both list and graph."""
        try:
            user_id = self.controller.current_user_id
            
            # Clear records list
            for widget in self.records_container.winfo_children():
                widget.destroy()

            # Query records for current user
            if user_id:
                cursor.execute("SELECT id, date, total_kwh, total_cost FROM records WHERE user_id = ? ORDER BY date DESC", (user_id,))
            else:
                cursor.execute("SELECT id, date, total_kwh, total_cost FROM records WHERE user_id IS NULL ORDER BY date DESC")
            
            rows = cursor.fetchall()

            if not rows:
                no_data = ctk.CTkLabel(self.records_container, text="No records found", text_color="gray", font=("Arial", 11))
                no_data.pack(pady=20)
            else:
                # Display each record with delete button
                for rec in rows:
                    record_id, date, total_kwh, total_cost = rec
                    self.create_record_item(record_id, date, total_kwh, total_cost)

            # Update graph
            self.update_graph(rows)

        except Exception as e:
            print(f"[RecordsPage] Error refreshing records: {e}")

    def create_record_item(self, record_id, date, total_kwh, total_cost):
        """Create a record item with delete button."""
        item_frame = ctk.CTkFrame(self.records_container, fg_color="#2b2b2b", corner_radius=6)
        item_frame.pack(fill="x", pady=4, padx=4)

        # Record info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        date_label = ctk.CTkLabel(info_frame, text=date, font=("Arial", 10, "bold"), text_color="white")
        date_label.pack(anchor="w")

        kwh_label = ctk.CTkLabel(info_frame, text=f"{total_kwh:.2f} kWh", font=("Arial", 9), text_color="cyan")
        kwh_label.pack(anchor="w")

        cost_label = ctk.CTkLabel(info_frame, text=f"₱{total_cost:.2f}", font=("Arial", 9), text_color="#4CAF50")
        cost_label.pack(anchor="w")

        # Delete button
        delete_btn = ctk.CTkButton(
            item_frame,
            text="✕",
            width=30,
            height=30,
            fg_color="#d32f2f",
            hover_color="#c62828",
            command=lambda: self.delete_record(record_id, item_frame)
        )
        delete_btn.pack(side="right", padx=8, pady=8)

    def delete_record(self, record_id, item_widget):
        """Delete a record from database and remove from list."""
        try:
            # Delete record items first (foreign key)
            cursor.execute("DELETE FROM record_items WHERE record_id = ?", (record_id,))
            # Delete the record itself
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
            conn.commit()

            # Remove from UI
            item_widget.destroy()

            # Refresh graph
            self.refresh_graph_only()

            print(f"[RecordsPage] Deleted record {record_id}")
        except Exception as e:
            print(f"[RecordsPage] Error deleting record: {e}")

    def update_graph(self, rows):
        """Draw line graph with dates and kWh values."""
        try:
            # Clear previous canvas if exists
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

            if not rows:
                # No data - show empty message
                empty_label = ctk.CTkLabel(
                    self.canvas_frame,
                    text="No data to display",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(expand=True)
                return

            # Extract dates and kwh values
            dates = [row[1] for row in rows]  # date
            kwh_values = [row[2] if row[2] else 0 for row in rows]  # total_kwh

            # Reverse to show oldest first (left to right)
            dates = list(reversed(dates))
            kwh_values = list(reversed(kwh_values))

            # Create matplotlib figure
            self.figure = Figure(figsize=(6, 4), dpi=100, facecolor="#212121", edgecolor="white")
            ax = self.figure.add_subplot(111)
            ax.set_facecolor("#1a1a1a")

            # Plot line
            ax.plot(range(len(dates)), kwh_values, marker='o', linewidth=2, markersize=6, color="#1976d2")
            ax.fill_between(range(len(dates)), kwh_values, alpha=0.3, color="#1976d2")

            # Format axes
            ax.set_xlabel("Date", fontsize=10, color="white")
            ax.set_ylabel("kWh", fontsize=10, color="white")
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=8, color="white")
            ax.tick_params(axis='y', labelcolor='white')
            ax.grid(True, alpha=0.2, color="white")

            # Spine colors
            for spine in ax.spines.values():
                spine.set_color("white")

            self.figure.tight_layout()

            # Embed in tkinter
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            print(f"[RecordsPage] Error updating graph: {e}")

    def refresh_graph_only(self):
        """Refresh only the graph (used after deleting a record)."""
        try:
            user_id = self.controller.current_user_id
            if user_id:
                cursor.execute("SELECT id, date, total_kwh, total_cost FROM records WHERE user_id = ? ORDER BY date DESC", (user_id,))
            else:
                cursor.execute("SELECT id, date, total_kwh, total_cost FROM records WHERE user_id IS NULL ORDER BY date DESC")
            rows = cursor.fetchall()
            self.update_graph(rows)
        except Exception as e:
            print(f"[RecordsPage] Error refreshing graph: {e}")

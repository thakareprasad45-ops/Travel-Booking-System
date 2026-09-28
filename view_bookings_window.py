"""
view_bookings_window.py
------------------------
Shows all bookings made by the logged-in user, including their
current status (Pending / Confirmed / Rejected / Cancelled) and
any note left by the admin. Users can cancel a Pending or
Confirmed booking themselves.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database as db


class ViewBookingsWindow:
    def __init__(self, master, user_id):
        self.master = master
        self.user_id = user_id

        master.title("My Bookings")
        master.geometry("860x440")
        master.configure(bg="white")

        tk.Label(master, text="My Bookings", font=("Segoe UI", 14, "bold"),
                  bg="white", fg="#1a4d8f").pack(pady=(15, 10))

        table_frame = tk.Frame(master, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        columns = ("id", "name", "category", "date", "persons", "total", "status", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        headings = {
            "id": "Booking ID", "name": "Destination", "category": "Category",
            "date": "Travel Date", "persons": "Persons", "total": "Total (₹)",
            "status": "Status", "note": "Admin Note"
        }
        widths = {"id": 70, "name": 180, "category": 100, "date": 90,
                  "persons": 60, "total": 90, "status": 90, "note": 150}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        self.tree.tag_configure("Pending", background="#fff6e0")
        self.tree.tag_configure("Confirmed", background="#e6f7ea")
        self.tree.tag_configure("Rejected", background="#fde8e8")
        self.tree.tag_configure("Cancelled", background="#eeeeee")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = tk.Frame(master, bg="white")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        tk.Button(btn_frame, text="Cancel Selected Booking", bg="#c0392b", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.cancel_selected).pack(side="left")

        tk.Button(btn_frame, text="Refresh", bg="#1a4d8f", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.load_bookings).pack(side="left", padx=10)

        self.load_bookings()

    def load_bookings(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = db.get_user_bookings(self.user_id)
        for r in rows:
            booking_id, name, category, travel_date, persons, total, status, booking_date, note = r
            self.tree.insert("", "end",
                              values=(booking_id, name, category, travel_date, persons,
                                       f"{total:.2f}", status, note or "-"),
                              tags=(status,))

    def cancel_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking to cancel.")
            return

        values = self.tree.item(selected[0])["values"]
        booking_id, status = values[0], values[6]

        if status in ("Cancelled", "Rejected"):
            messagebox.showinfo("Not Allowed", f"This booking is already {status.lower()}.")
            return

        confirm = messagebox.askyesno("Confirm Cancellation",
                                       f"Cancel booking #{booking_id}?")
        if confirm:
            success, msg = db.cancel_booking(booking_id)
            if success:
                messagebox.showinfo("Cancelled", msg)
                self.load_bookings()
            else:
                messagebox.showerror("Error", msg)

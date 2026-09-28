"""
dashboard.py
------------
Main dashboard shown to a NORMAL USER after login. Lists
destinations/flights/hotels and lets the user book (booking is
created as 'Pending' and must be approved by the admin) or view
their own bookings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from booking_window import open_booking_window
from view_bookings_window import ViewBookingsWindow


class Dashboard(tk.Frame):
    def __init__(self, master, user_id, full_name, on_logout):
        super().__init__(master, bg="#eef3f8")
        self.master = master
        self.user_id = user_id
        self.full_name = full_name
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)

        self.build_header()
        self.build_filter_bar()
        self.build_destination_table()
        self.load_destinations()

    # ---------------- HEADER ---------------- #
    def build_header(self):
        header = tk.Frame(self, bg="#1a4d8f", height=70)
        header.pack(fill="x")

        tk.Label(header, text=f"✈  Welcome, {self.full_name}", bg="#1a4d8f", fg="white",
                  font=("Segoe UI", 14, "bold")).pack(side="left", padx=20, pady=15)

        tk.Button(header, text="My Bookings", bg="white", fg="#1a4d8f",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.open_my_bookings).pack(side="right", padx=10, pady=18)

        tk.Button(header, text="Logout", bg="#c0392b", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.on_logout).pack(side="right", padx=10, pady=18)

    # ---------------- FILTER BAR ---------------- #
    def build_filter_bar(self):
        bar = tk.Frame(self, bg="#eef3f8")
        bar.pack(fill="x", padx=20, pady=15)

        tk.Label(bar, text="Filter by category:", bg="#eef3f8",
                  font=("Segoe UI", 10, "bold")).pack(side="left")

        self.category_var = tk.StringVar(value="All")
        options = ["All", "Flight", "Hotel", "Tour Package"]
        dropdown = ttk.Combobox(bar, textvariable=self.category_var, values=options,
                                 state="readonly", width=15)
        dropdown.pack(side="left", padx=10)
        dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_destinations())

        tk.Label(bar, text="ℹ Bookings require admin approval before they're confirmed.",
                  bg="#eef3f8", fg="#888", font=("Segoe UI", 8, "italic")).pack(side="left", padx=15)

        tk.Button(bar, text="Book Selected", bg="#27ae60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.book_selected).pack(side="right")

    # ---------------- TABLE ---------------- #
    def build_destination_table(self):
        table_frame = tk.Frame(self, bg="#eef3f8")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("id", "name", "category", "source", "price", "seats")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = {
            "id": "ID", "name": "Name", "category": "Category",
            "source": "Source", "price": "Price (₹)", "seats": "Seats Left"
        }
        widths = {"id": 40, "name": 250, "category": 120, "source": 120, "price": 100, "seats": 90}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col != "name" else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_destinations(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        category = self.category_var.get()
        rows = db.get_all_destinations(category)
        for r in rows:
            dest_id, name, cat, source, price, seats, desc = r
            self.tree.insert("", "end", values=(dest_id, name, cat, source, f"{price:.2f}", seats))

    def book_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a destination to book.")
            return
        dest_id = self.tree.item(selected[0])["values"][0]
        open_booking_window(self.master, self.user_id, dest_id, on_complete=self.load_destinations)

    def open_my_bookings(self):
        top = tk.Toplevel(self.master)
        ViewBookingsWindow(top, self.user_id)

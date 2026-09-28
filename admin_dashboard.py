"""
admin_dashboard.py
-------------------
Dashboard shown when a user with is_admin=1 logs in.

Tabs:
    1. Bookings   -> view ALL bookings from ALL users, approve/reject
                     Pending ones (human review happens here)
    2. Users      -> read-only list of registered users
    3. Destinations -> add or remove flights/hotels/tour packages
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database as db


class AdminDashboard(tk.Frame):
    def __init__(self, master, admin_name, on_logout):
        super().__init__(master, bg="#eef3f8")
        self.master = master
        self.admin_name = admin_name
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)

        self.build_header()
        self.build_summary_bar()
        self.build_tabs()

    # ---------------- HEADER ---------------- #
    def build_header(self):
        header = tk.Frame(self, bg="#0f2e5c", height=70)
        header.pack(fill="x")

        tk.Label(header, text=f"🛠  Admin Panel — {self.admin_name}", bg="#0f2e5c", fg="white",
                  font=("Segoe UI", 14, "bold")).pack(side="left", padx=20, pady=15)

        tk.Button(header, text="Logout", bg="#c0392b", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.on_logout).pack(side="right", padx=15, pady=18)

    # ---------------- SUMMARY BAR ---------------- #
    def build_summary_bar(self):
        self.summary_frame = tk.Frame(self, bg="#eef3f8")
        self.summary_frame.pack(fill="x", padx=20, pady=(15, 0))
        self.refresh_summary()

    def refresh_summary(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()

        counts = db.get_booking_counts()
        cards = [
            ("Pending Review", counts["Pending"], "#e67e22"),
            ("Confirmed", counts["Confirmed"], "#27ae60"),
            ("Rejected", counts["Rejected"], "#c0392b"),
            ("Cancelled", counts["Cancelled"], "#7f8c8d"),
        ]
        for label, value, color in cards:
            card = tk.Frame(self.summary_frame, bg=color, width=180, height=60)
            card.pack(side="left", padx=(0, 12))
            card.pack_propagate(False)
            tk.Label(card, text=str(value), bg=color, fg="white",
                      font=("Segoe UI", 16, "bold")).pack(pady=(6, 0))
            tk.Label(card, text=label, bg=color, fg="white",
                      font=("Segoe UI", 9)).pack()

    # ---------------- TABS ---------------- #
    def build_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.bookings_tab = tk.Frame(notebook, bg="white")
        self.users_tab = tk.Frame(notebook, bg="white")
        self.dest_tab = tk.Frame(notebook, bg="white")

        notebook.add(self.bookings_tab, text="  Bookings (Review & Approve)  ")
        notebook.add(self.users_tab, text="  Registered Users  ")
        notebook.add(self.dest_tab, text="  Manage Destinations  ")

        self.build_bookings_tab()
        self.build_users_tab()
        self.build_destinations_tab()

    # ================= BOOKINGS TAB ================= #
    def build_bookings_tab(self):
        top_bar = tk.Frame(self.bookings_tab, bg="white")
        top_bar.pack(fill="x", pady=(10, 5), padx=10)

        tk.Label(top_bar, text="Filter status:", bg="white",
                  font=("Segoe UI", 10, "bold")).pack(side="left")

        self.status_filter_var = tk.StringVar(value="Pending")
        filter_dropdown = ttk.Combobox(
            top_bar, textvariable=self.status_filter_var,
            values=["All", "Pending", "Confirmed", "Rejected", "Cancelled"],
            state="readonly", width=15
        )
        filter_dropdown.pack(side="left", padx=10)
        filter_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_bookings())

        tk.Button(top_bar, text="Refresh", bg="#1a4d8f", fg="white", relief="flat",
                  cursor="hand2", command=self.load_bookings).pack(side="left")

        table_frame = tk.Frame(self.bookings_tab, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "user", "dest", "category", "date", "persons", "total", "status", "note")
        self.bookings_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        headings = {
            "id": "ID", "user": "Booked By", "dest": "Destination", "category": "Category",
            "date": "Travel Date", "persons": "Persons", "total": "Total (₹)",
            "status": "Status", "note": "Admin Note"
        }
        widths = {"id": 40, "user": 130, "dest": 170, "category": 90, "date": 90,
                  "persons": 60, "total": 90, "status": 90, "note": 140}

        for col in columns:
            self.bookings_tree.heading(col, text=headings[col])
            self.bookings_tree.column(col, width=widths[col], anchor="center")

        self.bookings_tree.tag_configure("Pending", background="#fff6e0")
        self.bookings_tree.tag_configure("Confirmed", background="#e6f7ea")
        self.bookings_tree.tag_configure("Rejected", background="#fde8e8")
        self.bookings_tree.tag_configure("Cancelled", background="#eeeeee")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        self.bookings_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        action_bar = tk.Frame(self.bookings_tab, bg="white")
        action_bar.pack(fill="x", padx=10, pady=(0, 15))

        tk.Button(action_bar, text="✔ Approve Selected", bg="#27ae60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.approve_selected).pack(side="left")

        tk.Button(action_bar, text="✘ Reject Selected", bg="#c0392b", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.reject_selected).pack(side="left", padx=10)

        self.load_bookings()

    def load_bookings(self):
        for row in self.bookings_tree.get_children():
            self.bookings_tree.delete(row)

        status = self.status_filter_var.get()
        rows = db.get_all_bookings(status)
        for r in rows:
            (booking_id, full_name, username, dest_name, category, travel_date,
             persons, total, status_val, booking_date, dest_id, note) = r
            self.bookings_tree.insert(
                "", "end",
                values=(booking_id, f"{full_name} ({username})", dest_name, category,
                         travel_date, persons, f"{total:.2f}", status_val, note or "-"),
                tags=(status_val,)
            )
        self.refresh_summary()

    def _get_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking first.")
            return None
        values = self.bookings_tree.item(selected[0])["values"]
        return values  # (id, user, dest, category, date, persons, total, status, note)

    def approve_selected(self):
        values = self._get_selected_booking()
        if not values:
            return
        booking_id, status = values[0], values[7]

        if status != "Pending":
            messagebox.showinfo("Not Allowed", f"Only Pending bookings can be approved (this is {status}).")
            return

        confirm = messagebox.askyesno("Approve Booking", f"Approve booking #{booking_id}?")
        if not confirm:
            return

        note = simpledialog.askstring("Admin Note (optional)",
                                        "Add a note for the customer (optional):", parent=self.master)
        success, msg = db.approve_booking(booking_id, note or "")
        if success:
            messagebox.showinfo("Approved", msg)
            self.load_bookings()
        else:
            messagebox.showerror("Error", msg)

    def reject_selected(self):
        values = self._get_selected_booking()
        if not values:
            return
        booking_id, status = values[0], values[7]

        if status != "Pending":
            messagebox.showinfo("Not Allowed", f"Only Pending bookings can be rejected (this is {status}).")
            return

        confirm = messagebox.askyesno("Reject Booking", f"Reject booking #{booking_id}? Seats will be released.")
        if not confirm:
            return

        note = simpledialog.askstring("Reason for rejection (optional)",
                                        "Add a reason for the customer (optional):", parent=self.master)
        success, msg = db.reject_booking(booking_id, note or "")
        if success:
            messagebox.showinfo("Rejected", msg)
            self.load_bookings()
        else:
            messagebox.showerror("Error", msg)

    # ================= USERS TAB ================= #
    def build_users_tab(self):
        tk.Label(self.users_tab, text="Registered Users", font=("Segoe UI", 12, "bold"),
                  bg="white", fg="#1a4d8f").pack(pady=(10, 5), anchor="w", padx=10)

        table_frame = tk.Frame(self.users_tab, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "name", "username", "email", "phone")
        self.users_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {"id": "ID", "name": "Full Name", "username": "Username",
                    "email": "Email", "phone": "Phone"}
        widths = {"id": 50, "name": 180, "username": 140, "email": 200, "phone": 120}

        for col in columns:
            self.users_tree.heading(col, text=headings[col])
            self.users_tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(self.users_tab, text="Refresh", bg="#1a4d8f", fg="white", relief="flat",
                  cursor="hand2", command=self.load_users).pack(anchor="w", padx=10, pady=(0, 10))

        self.load_users()

    def load_users(self):
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)
        for u in db.get_all_users():
            self.users_tree.insert("", "end", values=u)

    # ================= DESTINATIONS TAB ================= #
    def build_destinations_tab(self):
        top = tk.Frame(self.dest_tab, bg="white")
        top.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top, text="Manage Destinations / Packages", font=("Segoe UI", 12, "bold"),
                  bg="white", fg="#1a4d8f").pack(side="left")

        tk.Button(top, text="+ Add New", bg="#27ae60", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self.open_add_destination_form).pack(side="right")

        table_frame = tk.Frame(self.dest_tab, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "name", "category", "source", "price", "seats")
        self.dest_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {"id": "ID", "name": "Name", "category": "Category",
                    "source": "Source", "price": "Price (₹)", "seats": "Seats Left"}
        widths = {"id": 40, "name": 220, "category": 110, "source": 110, "price": 90, "seats": 90}

        for col in columns:
            self.dest_tree.heading(col, text=headings[col])
            self.dest_tree.column(col, width=widths[col], anchor="center" if col != "name" else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.dest_tree.yview)
        self.dest_tree.configure(yscrollcommand=scrollbar.set)
        self.dest_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = tk.Frame(self.dest_tab, bg="white")
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(bottom, text="Delete Selected", bg="#c0392b", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self.delete_selected_destination).pack(side="left")

        tk.Button(bottom, text="Refresh", bg="#1a4d8f", fg="white", relief="flat",
                  cursor="hand2", command=self.load_destinations).pack(side="left", padx=10)

        self.load_destinations()

    def load_destinations(self):
        for row in self.dest_tree.get_children():
            self.dest_tree.delete(row)
        for d in db.get_all_destinations():
            dest_id, name, category, source, price, seats, desc = d
            self.dest_tree.insert("", "end", values=(dest_id, name, category, source,
                                                        f"{price:.2f}", seats))

    def delete_selected_destination(self):
        selected = self.dest_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a destination to delete.")
            return
        values = self.dest_tree.item(selected[0])["values"]
        dest_id, name = values[0], values[1]

        confirm = messagebox.askyesno("Confirm Delete",
                                       f"Delete '{name}'? This cannot be undone.")
        if confirm:
            db.delete_destination(dest_id)
            self.load_destinations()

    def open_add_destination_form(self):
        win = tk.Toplevel(self.master)
        win.title("Add New Destination")
        win.geometry("380x480")
        win.configure(bg="white")
        win.grab_set()

        tk.Label(win, text="Add New Destination", font=("Segoe UI", 13, "bold"),
                  bg="white", fg="#1a4d8f").pack(pady=(20, 15))

        fields = {}

        def add_field(label_text):
            tk.Label(win, text=label_text, bg="white", anchor="w").pack(fill="x", padx=30)
            entry = tk.Entry(win, font=("Segoe UI", 10))
            entry.pack(fill="x", padx=30, pady=(2, 10))
            fields[label_text] = entry
            return entry

        add_field("Name")

        tk.Label(win, text="Category", bg="white", anchor="w").pack(fill="x", padx=30)
        category_var = tk.StringVar(value="Tour Package")
        ttk.Combobox(win, textvariable=category_var,
                     values=["Flight", "Hotel", "Tour Package"],
                     state="readonly").pack(fill="x", padx=30, pady=(2, 10))

        add_field("Source (e.g. city)")
        add_field("Price (₹)")
        add_field("Seats Available")

        tk.Label(win, text="Description", bg="white", anchor="w").pack(fill="x", padx=30)
        desc_text = tk.Text(win, height=4, font=("Segoe UI", 10))
        desc_text.pack(fill="x", padx=30, pady=(2, 15))

        def save():
            try:
                name = fields["Name"].get().strip()
                source = fields["Source (e.g. city)"].get().strip()
                price = float(fields["Price (₹)"].get().strip())
                seats = int(fields["Seats Available"].get().strip())
                description = desc_text.get("1.0", "end").strip()
                category = category_var.get()

                if not name:
                    raise ValueError("Name is required.")

                db.add_destination(name, category, source, price, seats, description)
                messagebox.showinfo("Success", "Destination added successfully.")
                self.load_destinations()
                win.destroy()
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter valid Price and Seats numbers.")

        tk.Button(win, text="Save Destination", bg="#27ae60", fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  command=save).pack(fill="x", padx=30, ipady=6)

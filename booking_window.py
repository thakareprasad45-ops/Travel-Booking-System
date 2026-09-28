"""
booking_window.py
------------------
Popup Toplevel window used to submit a booking request for a
selected destination. The booking is created with status
'Pending' — seats are held immediately, but the booking only
becomes 'Confirmed' once an admin reviews and approves it.
"""

import tkinter as tk
from tkinter import messagebox
import database as db


def open_booking_window(master, user_id, dest_id, on_complete=None):
    dest = db.get_destination_by_id(dest_id)
    if not dest:
        messagebox.showerror("Error", "Destination not found.")
        return

    _, name, category, source, price, seats_available, description = dest

    win = tk.Toplevel(master)
    win.title(f"Book: {name}")
    win.geometry("420x490")
    win.configure(bg="white")
    win.resizable(False, False)
    win.grab_set()  # modal

    tk.Label(win, text=name, font=("Segoe UI", 14, "bold"), bg="white",
              fg="#1a4d8f", wraplength=380, justify="left").pack(pady=(20, 5), padx=20, anchor="w")

    tk.Label(win, text=f"{category}  •  From: {source or 'N/A'}", bg="white",
              fg="#555", font=("Segoe UI", 10)).pack(padx=20, anchor="w")

    tk.Label(win, text=description, bg="white", fg="#333", wraplength=380,
              justify="left", font=("Segoe UI", 9)).pack(padx=20, pady=(8, 15), anchor="w")

    tk.Label(win, text=f"Price per person: ₹{price:.2f}", bg="white",
              font=("Segoe UI", 10, "bold")).pack(padx=20, anchor="w")
    tk.Label(win, text=f"Seats available: {seats_available}", bg="white",
              font=("Segoe UI", 10)).pack(padx=20, anchor="w", pady=(0, 15))

    form = tk.Frame(win, bg="white")
    form.pack(fill="x", padx=20)

    tk.Label(form, text="Travel Date (YYYY-MM-DD):", bg="white", anchor="w").pack(fill="x")
    date_entry = tk.Entry(form, font=("Segoe UI", 11))
    date_entry.pack(fill="x", pady=(2, 10))

    tk.Label(form, text="Number of Persons:", bg="white", anchor="w").pack(fill="x")
    persons_var = tk.IntVar(value=1)
    persons_spin = tk.Spinbox(form, from_=1, to=max(seats_available, 1),
                                textvariable=persons_var, font=("Segoe UI", 11))
    persons_spin.pack(fill="x", pady=(2, 15))

    total_label = tk.Label(win, text=f"Total: ₹{price:.2f}", bg="white",
                             font=("Segoe UI", 12, "bold"), fg="#27ae60")
    total_label.pack(padx=20, anchor="w")

    tk.Label(win, text="⚠ This booking will be marked 'Pending' until an admin approves it.",
              bg="white", fg="#c0782b", font=("Segoe UI", 8, "italic"),
              wraplength=380, justify="left").pack(padx=20, pady=(6, 0), anchor="w")

    def update_total(*args):
        try:
            n = int(persons_var.get())
        except (tk.TclError, ValueError):
            n = 1
        total_label.config(text=f"Total: ₹{price * n:.2f}")

    persons_var.trace_add("write", update_total)

    def confirm_booking():
        travel_date = date_entry.get().strip()
        try:
            num_persons = int(persons_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number of persons.")
            return

        if not travel_date:
            messagebox.showwarning("Missing Date", "Please enter a travel date.")
            return

        if num_persons < 1 or num_persons > seats_available:
            messagebox.showwarning("Invalid Seats", f"Only {seats_available} seat(s) available.")
            return

        total_price = price * num_persons

        # Hold the seats immediately so two users can't overbook while pending
        if not db.update_seats(dest_id, num_persons):
            messagebox.showerror("Error", "Seats are no longer available.")
            return

        booking_id = db.create_booking(user_id, dest_id, travel_date, num_persons, total_price)

        messagebox.showinfo(
            "Booking Submitted",
            f"Booking #{booking_id} submitted!\nTotal: ₹{total_price:.2f}\n\n"
            "Status: PENDING — an admin will review and confirm your booking."
        )
        if on_complete:
            on_complete()
        win.destroy()

    btn_frame = tk.Frame(win, bg="white")
    btn_frame.pack(fill="x", padx=20, pady=20, side="bottom")

    tk.Button(btn_frame, text="Submit Booking Request", bg="#27ae60", fg="white",
              font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
              command=confirm_booking).pack(fill="x", ipady=6, pady=(0, 8))

    tk.Button(btn_frame, text="Cancel", bg="#eee", fg="#333", relief="flat",
              cursor="hand2", command=win.destroy).pack(fill="x", ipady=4)

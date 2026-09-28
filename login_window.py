"""
login_window.py
----------------
Tkinter Login and Registration screen for the Travel Booking System.

The SAME login form is used for both normal users and the admin —
after authentication, database.py tells us whether the account is
an admin (is_admin flag), and main.py routes to the correct dashboard.

Default admin account (seeded automatically on first run):
    username: admin
    password: admin123
"""

import tkinter as tk
from tkinter import messagebox
import database as db


class LoginWindow(tk.Frame):
    def __init__(self, master, on_login_success):
        """
        on_login_success(user_id, full_name, is_admin) is called after a
        successful login so main.py can route to the right dashboard.
        """
        super().__init__(master, bg="#eef3f8")
        self.master = master
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        self.build_login_ui()

    # ---------------- LOGIN UI ---------------- #
    def build_login_ui(self):
        self.clear_frame()

        card = tk.Frame(self, bg="white", bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=440)

        tk.Label(card, text="✈  Travel Booking System", font=("Segoe UI", 15, "bold"),
                  bg="white", fg="#1a4d8f").pack(pady=(30, 5))
        tk.Label(card, text="Login to your account", font=("Segoe UI", 10),
                  bg="white", fg="#555").pack(pady=(0, 20))

        tk.Label(card, text="Username", bg="white", anchor="w").pack(fill="x", padx=40)
        self.username_entry = tk.Entry(card, font=("Segoe UI", 11))
        self.username_entry.pack(fill="x", padx=40, pady=(2, 12))

        tk.Label(card, text="Password", bg="white", anchor="w").pack(fill="x", padx=40)
        self.password_entry = tk.Entry(card, font=("Segoe UI", 11), show="*")
        self.password_entry.pack(fill="x", padx=40, pady=(2, 20))

        login_btn = tk.Button(card, text="Login", bg="#1a4d8f", fg="white",
                               font=("Segoe UI", 11, "bold"), relief="flat",
                               command=self.handle_login, cursor="hand2")
        login_btn.pack(fill="x", padx=40, ipady=6)

        tk.Label(card, text="Don't have an account?", bg="white",
                  font=("Segoe UI", 9)).pack(pady=(18, 0))

        signup_btn = tk.Button(card, text="Create New Account", bg="white", fg="#1a4d8f",
                                relief="flat", font=("Segoe UI", 10, "underline"),
                                cursor="hand2", command=self.build_register_ui)
        signup_btn.pack()

        tk.Label(card, text="Admin? Use your admin username & password above.",
                  bg="white", font=("Segoe UI", 8), fg="#999").pack(pady=(15, 0))

        self.master.bind("<Return>", lambda e: self.handle_login())

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")
            return

        user = db.authenticate_user(username, password)
        if user:
            user_id, full_name, uname, is_admin = user
            self.on_login_success(user_id, full_name, bool(is_admin))
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # ---------------- REGISTER UI (normal users only) ---------------- #
    def build_register_ui(self):
        self.clear_frame()

        card = tk.Frame(self, bg="white", bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=560)

        tk.Label(card, text="Create New Account", font=("Segoe UI", 15, "bold"),
                  bg="white", fg="#1a4d8f").pack(pady=(25, 15))

        fields = [("Full Name", "full_name"), ("Username", "username"),
                  ("Password", "password"), ("Email", "email"), ("Phone", "phone")]
        self.reg_entries = {}

        for label_text, key in fields:
            tk.Label(card, text=label_text, bg="white", anchor="w").pack(fill="x", padx=40)
            show_char = "*" if key == "password" else ""
            entry = tk.Entry(card, font=("Segoe UI", 11), show=show_char)
            entry.pack(fill="x", padx=40, pady=(2, 10))
            self.reg_entries[key] = entry

        reg_btn = tk.Button(card, text="Register", bg="#1a4d8f", fg="white",
                             font=("Segoe UI", 11, "bold"), relief="flat",
                             command=self.handle_register, cursor="hand2")
        reg_btn.pack(fill="x", padx=40, pady=(10, 10), ipady=6)

        back_btn = tk.Button(card, text="← Back to Login", bg="white", fg="#1a4d8f",
                              relief="flat", font=("Segoe UI", 10, "underline"),
                              cursor="hand2", command=self.build_login_ui)
        back_btn.pack()

    def handle_register(self):
        values = {k: e.get().strip() for k, e in self.reg_entries.items()}

        if not values["full_name"] or not values["username"] or not values["password"]:
            messagebox.showwarning("Missing Fields", "Full name, username and password are required.")
            return

        success, msg = db.register_user(
            values["full_name"], values["username"], values["password"],
            values["email"], values["phone"]
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.build_login_ui()
        else:
            messagebox.showerror("Error", msg)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

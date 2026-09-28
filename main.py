"""
main.py
-------
Entry point for the Travel Booking System (Tkinter GUI app).

Run with:
    python main.py

Default admin login (auto-created on first run):
    username: admin
    password: admin123
"""

import tkinter as tk
import database as db
from login_window import LoginWindow
from dashboard import Dashboard
from admin_dashboard import AdminDashboard


class TravelBookingApp:
    def __init__(self):
        db.initialize_database()

        self.root = tk.Tk()
        self.root.title("Travel Booking System")
        self.root.geometry("1000x650")
        self.root.minsize(900, 580)

        self.current_frame = None
        self.show_login()
        self.root.mainloop()

    def show_login(self):
        self.clear_current_frame()
        self.current_frame = LoginWindow(self.root, on_login_success=self.route_after_login)

    def route_after_login(self, user_id, full_name, is_admin):
        if is_admin:
            self.show_admin_dashboard(full_name)
        else:
            self.show_user_dashboard(user_id, full_name)

    def show_user_dashboard(self, user_id, full_name):
        self.clear_current_frame()
        self.current_frame = Dashboard(self.root, user_id, full_name, on_logout=self.show_login)

    def show_admin_dashboard(self, full_name):
        self.clear_current_frame()
        self.current_frame = AdminDashboard(self.root, full_name, on_logout=self.show_login)

    def clear_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.root.unbind("<Return>")


if __name__ == "__main__":
    TravelBookingApp()

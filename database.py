"""
database.py
------------
Handles all database creation and operations for the
Travel Booking System using SQLite3.

Booking workflow:
    User books  ->  status = 'Pending'
    Admin approves  ->  status = 'Confirmed'
    Admin rejects    ->  status = 'Rejected'  (seats restored)
    User cancels      ->  status = 'Cancelled' (seats restored)
"""

import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "travel_booking.db")

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def get_connection():
    """Return a new SQLite connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create all required tables and seed sample data + default admin."""
    conn = get_connection()
    cur = conn.cursor()

    # Users table (is_admin: 0 = normal user, 1 = admin)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Destinations / packages table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            dest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,      -- Flight / Hotel / Tour Package
            source TEXT,
            price REAL NOT NULL,
            seats_available INTEGER NOT NULL,
            description TEXT
        )
    """)

    # Bookings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dest_id INTEGER NOT NULL,
            travel_date TEXT NOT NULL,
            num_persons INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',   -- Pending / Confirmed / Rejected / Cancelled
            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
            admin_note TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (dest_id) REFERENCES destinations(dest_id)
        )
    """)

    conn.commit()

    # Seed sample destinations only if table is empty
    cur.execute("SELECT COUNT(*) FROM destinations")
    if cur.fetchone()[0] == 0:
        sample_data = [
            ("Goa Beach Getaway", "Tour Package", "Mumbai", 8999.0, 30,
             "3 nights / 4 days beach resort package with breakfast."),
            ("Manali Snow Adventure", "Tour Package", "Delhi", 12999.0, 25,
             "4 nights / 5 days hill station trip with adventure sports."),
            ("Delhi to Dubai", "Flight", "Delhi", 24500.0, 60,
             "Round trip economy flight, 2 checked bags included."),
            ("Mumbai to London", "Flight", "Mumbai", 55999.0, 40,
             "Round trip economy flight with one stopover."),
            ("Taj Heritage Hotel, Agra", "Hotel", "Agra", 4500.0, 15,
             "Deluxe room per night, near Taj Mahal, free breakfast."),
            ("Kerala Backwaters Houseboat", "Hotel", "Alleppey", 6500.0, 10,
             "Overnight houseboat stay with all meals included."),
            ("Bangalore to Singapore", "Flight", "Bangalore", 32999.0, 50,
             "Round trip economy flight, direct."),
            ("Rajasthan Royal Tour", "Tour Package", "Jaipur", 15999.0, 20,
             "5 nights / 6 days covering Jaipur, Udaipur, Jodhpur."),
        ]
        cur.executemany("""
            INSERT INTO destinations (name, category, source, price, seats_available, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_data)
        conn.commit()

    # Seed default admin account only if no admin exists yet
    cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO users (full_name, username, password, email, phone, is_admin)
            VALUES (?, ?, ?, ?, ?, 1)
        """, ("Administrator", DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, "", ""))
        conn.commit()

    conn.close()


# ---------------- USER OPERATIONS ---------------- #

def register_user(full_name, username, password, email, phone):
    """Registers a normal (non-admin) user. Admin accounts cannot be created from the UI."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (full_name, username, password, email, phone, is_admin)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (full_name, username, password, email, phone))
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    finally:
        conn.close()


def authenticate_user(username, password):
    """Returns (user_id, full_name, username, is_admin) or None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, full_name, username, is_admin FROM users
        WHERE username = ? AND password = ?
    """, (username, password))
    row = cur.fetchone()
    conn.close()
    return row


def get_all_users():
    """Admin: list of all normal (non-admin) users."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, full_name, username, email, phone
        FROM users WHERE is_admin = 0
        ORDER BY full_name
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------- DESTINATION OPERATIONS ---------------- #

def get_all_destinations(category=None):
    conn = get_connection()
    cur = conn.cursor()
    if category and category != "All":
        cur.execute("SELECT * FROM destinations WHERE category = ?", (category,))
    else:
        cur.execute("SELECT * FROM destinations")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_destination_by_id(dest_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM destinations WHERE dest_id = ?", (dest_id,))
    row = cur.fetchone()
    conn.close()
    return row


def add_destination(name, category, source, price, seats_available, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO destinations (name, category, source, price, seats_available, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, source, price, seats_available, description))
    conn.commit()
    conn.close()


def delete_destination(dest_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM destinations WHERE dest_id = ?", (dest_id,))
    conn.commit()
    conn.close()


def update_seats(dest_id, seats_booked):
    """Deduct seats immediately when a booking request is made (held while Pending)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE destinations
        SET seats_available = seats_available - ?
        WHERE dest_id = ? AND seats_available >= ?
    """, (seats_booked, dest_id, seats_booked))
    conn.commit()
    success = cur.rowcount > 0
    conn.close()
    return success


def restore_seats(dest_id, seats_to_restore):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE destinations SET seats_available = seats_available + ?
        WHERE dest_id = ?
    """, (seats_to_restore, dest_id))
    conn.commit()
    conn.close()


# ---------------- BOOKING OPERATIONS (USER SIDE) ---------------- #

def create_booking(user_id, dest_id, travel_date, num_persons, total_price):
    """Creates a booking with status 'Pending' — awaiting admin review."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings (user_id, dest_id, travel_date, num_persons, total_price, status)
        VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (user_id, dest_id, travel_date, num_persons, total_price))
    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id


def get_user_bookings(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.booking_id, d.name, d.category, b.travel_date,
               b.num_persons, b.total_price, b.status, b.booking_date, b.admin_note
        FROM bookings b
        JOIN destinations d ON b.dest_id = d.dest_id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def cancel_booking(booking_id):
    """User cancels their own Pending or Confirmed booking; seats are restored."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT dest_id, num_persons, status FROM bookings WHERE booking_id = ?", (booking_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Booking not found."

    dest_id, num_persons, status = row
    if status in ("Cancelled", "Rejected"):
        conn.close()
        return False, f"Booking is already {status.lower()}."

    cur.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ?", (booking_id,))
    cur.execute("UPDATE destinations SET seats_available = seats_available + ? WHERE dest_id = ?",
                (num_persons, dest_id))
    conn.commit()
    conn.close()
    return True, "Booking cancelled successfully."


# ---------------- BOOKING OPERATIONS (ADMIN SIDE) ---------------- #

def get_all_bookings(status_filter=None):
    """Admin: view every booking from every user, optionally filtered by status."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT b.booking_id, u.full_name, u.username, d.name, d.category,
               b.travel_date, b.num_persons, b.total_price, b.status,
               b.booking_date, b.dest_id, b.admin_note
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN destinations d ON b.dest_id = d.dest_id
    """
    params = ()
    if status_filter and status_filter != "All":
        query += " WHERE b.status = ?"
        params = (status_filter,)
    query += " ORDER BY b.booking_date DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def approve_booking(booking_id, admin_note=""):
    """Admin confirms a Pending booking. Seats stay deducted (already held)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM bookings WHERE booking_id = ?", (booking_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Booking not found."
    if row[0] != "Pending":
        conn.close()
        return False, f"Only Pending bookings can be approved (current status: {row[0]})."

    cur.execute("UPDATE bookings SET status = 'Confirmed', admin_note = ? WHERE booking_id = ?",
                (admin_note, booking_id))
    conn.commit()
    conn.close()
    return True, "Booking approved and confirmed."


def reject_booking(booking_id, admin_note=""):
    """Admin rejects a Pending booking. Seats are released back to the pool."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, dest_id, num_persons FROM bookings WHERE booking_id = ?", (booking_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Booking not found."
    status, dest_id, num_persons = row
    if status != "Pending":
        conn.close()
        return False, f"Only Pending bookings can be rejected (current status: {status})."

    cur.execute("UPDATE bookings SET status = 'Rejected', admin_note = ? WHERE booking_id = ?",
                (admin_note, booking_id))
    cur.execute("UPDATE destinations SET seats_available = seats_available + ? WHERE dest_id = ?",
                (num_persons, dest_id))
    conn.commit()
    conn.close()
    return True, "Booking rejected and seats released."


def get_booking_counts():
    """Admin dashboard summary counts by status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM bookings GROUP BY status")
    rows = dict(cur.fetchall())
    conn.close()
    return {
        "Pending": rows.get("Pending", 0),
        "Confirmed": rows.get("Confirmed", 0),
        "Rejected": rows.get("Rejected", 0),
        "Cancelled": rows.get("Cancelled", 0),
    }

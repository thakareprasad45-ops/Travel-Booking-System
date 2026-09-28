# Travel Booking System (Tkinter + SQLite)

A desktop GUI application for booking flights, hotels, and tour packages,
with a full **Admin Approval Workflow** — every booking is reviewed by
an admin before it's confirmed.

## Features

### User side
- Register and log in
- Browse destinations (Flights / Hotels / Tour Packages) with filtering
- Submit a booking request (pick travel date + number of persons, total auto-calculated)
- Every booking starts as **Pending** and waits for admin approval
- "My Bookings" screen shows live status: Pending / Confirmed / Rejected / Cancelled,
  plus any note the admin left
- Cancel a Pending or Confirmed booking any time (seats are released back)

### Admin side (human review)
- Same login screen — logging in with the admin account opens the **Admin Panel** instead
- Dashboard summary cards: counts of Pending / Confirmed / Rejected / Cancelled bookings
- **Bookings tab**: see every booking from every user, filter by status,
  **Approve** or **Reject** each Pending request (with an optional note sent to the user)
- **Registered Users tab**: read-only list of everyone who has signed up
- **Manage Destinations tab**: add new flights/hotels/packages or delete existing ones

### Default admin login (auto-created on first run)
```
Username: admin
Password: admin123
```
Change this password directly in the database (or add a "change password"
feature) before using this in anything beyond a demo/college project.

## How booking approval works (the core workflow)

```
User submits booking  ─────────────►  status = "Pending"
                                        (seats are held immediately)
                                              |
                          Admin reviews in "Bookings" tab
                                              |
                     -----------------------------------------------------
                     |                                                   |
              Admin clicks Approve                             Admin clicks Reject
                     |                                                   |
          status = "Confirmed"                              status = "Rejected"
          (seats stay held)                                (seats released back)
```
Users can also cancel their own Pending/Confirmed booking at any time,
which releases the seats back to the pool.

## Project Structure
```
travel_booking_system/
├── main.py                   # Entry point - run this file, routes to user/admin dashboard
├── database.py                # SQLite setup + all DB queries (users, destinations, bookings)
├── login_window.py            # Login and registration screens (shared by user & admin)
├── dashboard.py                # USER dashboard - browse & book destinations
├── booking_window.py          # Booking request popup (creates a Pending booking)
├── view_bookings_window.py    # USER "My Bookings" - track status, cancel
├── admin_dashboard.py         # ADMIN panel - approve/reject bookings, manage users & destinations
├── requirements.txt
└── README.md
```

## Requirements
- Python 3.8+
- Tkinter (included with standard Python installs on Windows/Mac;
  on Linux install with `sudo apt install python3-tk` if missing)

No external pip packages are required — everything uses the Python
standard library (`tkinter`, `sqlite3`).

## How to Run
1. Extract/copy the `travel_booking_system` folder.
2. Open a terminal inside the folder.
3. Run:
   ```
   python main.py
   ```
4. On first run, `travel_booking.db` is created automatically with
   sample destinations and the default admin account already loaded.
5. **As a customer**: register a new account, log in, browse, and submit a booking.
6. **As the admin**: log out, log back in with `admin` / `admin123`,
   open the Bookings tab, and Approve/Reject pending requests.

## Do you need MySQL?

No. This project uses **SQLite**, a serverless file-based database
(`travel_booking.db` is created automatically next to the code — no
installation or setup required). SQLite is the right fit for a single-machine
desktop app like this one. You'd only need MySQL (or another server
database) if you converted this into a **multi-computer / web-based**
system where many people access the same server over a network at once.

## Notes
- Passwords are stored as plain text in this educational version.
  For production use, hash passwords (e.g. with `hashlib` or `bcrypt`).
- Travel dates are entered as free text in `YYYY-MM-DD` format;
  you can swap in `tkcalendar` for a date picker if desired.
- Only one admin account is auto-seeded; the registration form only
  creates normal (non-admin) users by design, for security.
"# Travel-Booking-System" 

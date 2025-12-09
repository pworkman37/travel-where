#Database implementation with test inserts

import sqlite3
import pandas as pd

# Create/Connect to a database file
conn = sqlite3.connect("my_database.db")
cur = conn.cursor()

# --- Create tables (SQLite compatible) ---

cur.execute("""
CREATE TABLE User (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    created_at     TEXT DEFAULT (CURRENT_TIMESTAMP)
);
""")

cur.execute("""
CREATE TABLE Trip (
    trip_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    trip_name    TEXT,
    start_date   TEXT,
    end_date     TEXT,
    total_price  REAL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);
""")

cur.execute("""
CREATE TABLE Destination (
    destination_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    city            TEXT NOT NULL,
    country         TEXT NOT NULL,
    description     TEXT
);
""")

cur.execute("""
CREATE TABLE Transportation (
    transportation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    type               TEXT CHECK(type IN ('flight','bus','train')) NOT NULL,
    company            TEXT,
    departure_location TEXT,
    arrival_location   TEXT,
    departure_time     TEXT,
    arrival_time       TEXT,
    price              REAL
);
""")

cur.execute("""
CREATE TABLE Shelter (
    shelter_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id    INTEGER NOT NULL,
    name              TEXT NOT NULL,
    type              TEXT,
    star_rating       INTEGER,
    price_per_night   REAL,
    FOREIGN KEY (destination_id) REFERENCES Destination(destination_id)
);
""")

cur.execute("""
CREATE TABLE TripDestination (
    trip_destination_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id              INTEGER NOT NULL,
    destination_id       INTEGER NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES Trip(trip_id),
    FOREIGN KEY (destination_id) REFERENCES Destination(destination_id)
);
""")

cur.execute("""
CREATE TABLE TripTransportation (
    trip_transportation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id                 INTEGER NOT NULL,
    transportation_id       INTEGER NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES Trip(trip_id),
    FOREIGN KEY (transportation_id) REFERENCES Transportation(transportation_id)
);
""")

# --- Insert sample data into each table ---

# User
cur.execute("""
INSERT INTO User (username, email, password_hash)
VALUES ('jayden123', 'jayden@example.com', 'hashed_password_here');
""")

# Trip
cur.execute("""
INSERT INTO Trip (user_id, trip_name, start_date, end_date, total_price)
VALUES (1, 'Summer Europe Trip', '2025-06-01', '2025-06-20', 2500.00);
""")

# Destination
cur.execute("""
INSERT INTO Destination (city, country, description)
VALUES ('Paris', 'France', 'City of Light');
""")

# Transportation
cur.execute("""
INSERT INTO Transportation (type, company, departure_location, arrival_location, departure_time, arrival_time, price)
VALUES ('flight', 'Air France', 'New York', 'Paris', '2025-06-01 18:00', '2025-06-02 07:30', 850.00);
""")

# Shelter
cur.execute("""
INSERT INTO Shelter (destination_id, name, type, star_rating, price_per_night)
VALUES (1, 'Hotel Lumiere', 'Hotel', 4, 150.00);
""")

# TripDestination
cur.execute("""
INSERT INTO TripDestination (trip_id, destination_id)
VALUES (1, 1);
""")

# TripTransportation
cur.execute("""
INSERT INTO TripTransportation (trip_id, transportation_id)
VALUES (1, 1);
""")

conn.commit()

# View all tables
df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
df

import mariadb

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "port": 3306,
    "database": "TravelAgency",
}

SQL_INIT_SCRIPT = """

CREATE DATABASE IF NOT EXISTS TravelAgency;
USE TravelAgency;

CREATE TABLE IF NOT EXISTS Location (
    LocationID INT PRIMARY KEY AUTO_INCREMENT,
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100),
    Pincode VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS Route (
    RouteID INT PRIMARY KEY AUTO_INCREMENT,
    SourceID INT NOT NULL,
    DestinationID INT NOT NULL,
    Distance DECIMAL(6,2),
    EstimatedTime VARCHAR(20),
    FOREIGN KEY (SourceID) REFERENCES Location(LocationID),
    FOREIGN KEY (DestinationID) REFERENCES Location(LocationID)
);

CREATE TABLE IF NOT EXISTS Bus (
    BusID INT PRIMARY KEY AUTO_INCREMENT,
    BusNumber VARCHAR(20) UNIQUE NOT NULL,
    Capacity INT NOT NULL,
    BusType ENUM('AC', 'Non-AC') NOT NULL,
    RouteID INT NOT NULL,
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID)
);

CREATE TABLE IF NOT EXISTS Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FullName VARCHAR(100) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(15),
    Gender ENUM('Male', 'Female', 'Other'),
    DateOfBirth DATE
);

CREATE TABLE IF NOT EXISTS Admin (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Email VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Role ENUM('Driver', 'Conductor', 'Cleaner', 'Other') NOT NULL,
    Phone VARCHAR(15),
    Address VARCHAR(255),
    DateOfJoining DATE
);

CREATE TABLE IF NOT EXISTS Trip (
    TripID INT PRIMARY KEY AUTO_INCREMENT,
    RouteID INT NOT NULL,
    BusID INT NOT NULL,
    DepartureTime DATETIME NOT NULL,
    ArrivalTime DATETIME,
    TripDate DATE NOT NULL,
    AvailableSeats INT,
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID),
    FOREIGN KEY (BusID) REFERENCES Bus(BusID)
);

CREATE TABLE IF NOT EXISTS Booking (
    BookingID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    TripID INT NOT NULL,
    BookingDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    TotalSeats INT NOT NULL,
    TotalAmount DECIMAL(8,2),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (TripID) REFERENCES Trip(TripID)
);

CREATE TABLE IF NOT EXISTS Seat (
    SeatID INT PRIMARY KEY AUTO_INCREMENT,
    TripID INT NOT NULL,
    SeatNumber VARCHAR(10) NOT NULL,
    Status ENUM('Available', 'Booked') DEFAULT 'Available',
    BookingID INT DEFAULT NULL,
    FOREIGN KEY (TripID) REFERENCES Trip(TripID),
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
);

CREATE TABLE IF NOT EXISTS Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL UNIQUE,
    Amount DECIMAL(8,2) NOT NULL,
    PaymentMethod ENUM('UPI', 'Card', 'Netbanking') NOT NULL,
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
);

CREATE TABLE IF NOT EXISTS Review (
    ReviewID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    BookingID INT NOT NULL,
    Rating DECIMAL(2,1) CHECK (Rating BETWEEN 0 AND 5),
    Comment TEXT,
    ReviewDate DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
);
"""


def get_connection():
    return mariadb.connect(**DB_CONFIG)


def initialize_database():
    try:
        conn = mariadb.connect(
            host="localhost",
            user="root",
            password="root",
            port=3306,
        )
        cur = conn.cursor()
        for statement in SQL_INIT_SCRIPT.strip().split(";"):
            if statement.strip():
                cur.execute(statement)
        conn.commit()
        print("[DB]: Initialised Successfully")
    except mariadb.Error as e:
        print(f"[DB]: Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

# Clinic Management System

A robust, role-based web application for managing clinic appointments and medical records, built with Django.

## 🚀 Project Overview

This system streamlines clinic operations by allowing patients to book appointments and doctors to manage their schedules and create medical records. Critical healthcare workflows—such as double-booking prevention, record immutability, and role-based access control—are enforced at the architecture level.

## ✨ Features

### For Patients
- **Secure Registration & Login**: Create an account with profile details.
- **Smart Appointment Booking**: 
    - Calendar-based scheduling.
    - Real-time validation prevents booking past dates or double-booking a doctor.
- **Dashboard**: View upcoming and past appointments.
- **Medical History**: Access read-only medical records created by doctors.

### For Doctors
- **Professional Dashboard**:
    - "Today's Schedule" view for immediate focus.
    - Categorized lists: Pending, Upcoming, Completed.
- **Appointment Management**:
    - Confirm pending requests.
    - Complete appointments (triggering record creation).
    - Cancel appointments with tracking.
- **Medical Records**:
    - Create diagnosis and notes for completed visits.
    - System prevents editing records once created (Immutability).

### For Admins
- **Operations Panel**: Full control over Users, Appointments, and Records via Django Admin.
- **Search & Filters**: Advanced filtering/searching for all data types.

## 🛠️ Technology Stack

- **Backend**: Django 5.x (Python 3.12)
- **Database**: PostgreSQL / SQLite (Development)
- **Frontend**: Django Templates + CSS + Vanilla JS
- **Styling**: Custom CSS with semantic HTML5
- **Testing**: Django Test Suite (`unittest` based)

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- `pip` and `venv`

### Local Development Reference

1.  **Clone the repository** (if applicable) and navigate to root.

2.  **Create and activate virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate   # Windows
    ```

3.  **Install dependencies**:
    ```bash
    pip install django psycopg2-binary
    ```

4.  **Apply Migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Create Superuser** (for Admin access):
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run Server**:
    ```bash
    python manage.py runserver
    ```
    Access the app at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 🧪 Testing

The project includes a comprehensive test suite covering authentication, appointment logic, and permission boundaries.

**Run all tests:**
```bash
python manage.py test apps.accounts apps.appointments apps.records
```

## 🔒 Security Highlights

- **Role-Based Access Control (RBAC)**: Custom Mixins (`PatientRequiredMixin`, `DoctorRequiredMixin`) ensure users never access unauthorized views.
- **Data Integrity**: Medical records are immutable. Appointments have status state machines (Pending -> Confirmed -> Completed).
- **Validation**: Server-side checks for date logic prevent "time-travel" bookings or conflicts.
- **CSRF Protection**: All forms use Django's CSRF tokens.

## 📸 Workflows

1.  **Booking**: Patient logs in -> Dashboard -> "Book Appointment" -> Select Doctor/Time -> Submit (Status: PENDING).
2.  **Confirmation**: Doctor logs in -> Dashboard -> Sees "Pending" -> Clicks "Confirm" (Status: CONFIRMED).
3.  **Completion**: Visit happens -> Doctor clicks "Complete" (Status: COMPLETED).
4.  **Record**: Doctor clicks "Create Record" on completed item -> Enters Diagnosis/Notes -> Save.
5.  **History**: Patient sees new Record link on Dashboard -> Views Details (Read-only).

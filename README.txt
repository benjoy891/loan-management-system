Here is the content in a more presentable format:

---

# Loan Management System

## Overview

The **Loan Management System** is a Django-based REST API designed to manage loans with user-defined monthly compound interest. The system provides role-based authentication, automatic interest calculations, and loan repayment schedules. It supports loan foreclosure, allowing users to settle loans before tenure completion with adjusted interest calculations. The system is built using Django and Django REST Framework (DRF), with authentication managed via JWT and OTP verification through Nodemailer.

## Features

- **User Authentication**: Secure registration and login system with OTP verification.
- **Loan Management**: Apply for loans, track repayments, and manage outstanding balances.
- **Interest Calculation**: Automatic computation of loan interest and penalties.
- **Loan Foreclosure**: Pay off loans early with adjusted interest.
- **Admin Panel**: Manage users, loans, and transactions via Django’s built-in admin interface.
- **Role-Based Access**: Different levels of access for customers, admins, and loan officers.

## Tech Stack

- **Backend**: Django, Django REST Framework (DRF)
- **Authentication**: JWT (Simple JWT)
- **OTP Email Service**: Nodemailer (via SMTP)
- **Database**: PostgreSQL (Preferred) or MongoDB (Optional with Djongo)
- **Deployment**: Render (Free Tier)

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL
- Node.js (for email service)

### Setup Instructions

1. **Clone the Repository**

    ```sh
    git clone https://github.com/yourusername/loan-management-system.git
    cd loan-management-system
    ```

2. **Set Up Virtual Environment**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```sh
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Create a **.env** file in the root directory and configure the following variables:

    ```
    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=your_database_host
    DB_PORT=5432
    SECRET_KEY=your_django_secret_key
    SMTP_HOST=smtp.yourprovider.com
    SMTP_PORT=587
    SMTP_USER=your_email@example.com
    SMTP_PASS=your_email_password
    ```

5. **Apply Migrations**

    ```sh
    python manage.py migrate
    ```

6. **Create Superuser**

    ```sh
    python manage.py createsuperuser
    ```

7. **Start the Django Server**

    ```sh
    python manage.py runserver
    ```

8. **Run Email Service (Node.js)**

    Navigate to the **emailService.js** file and install dependencies:

    ```sh
    cd email_service  # If email service is in a separate directory
    npm install
    node emailService.js
    ```

## Deployment

This project is deployed on **Render**.

### Running on Render:

- Ensure the database credentials match Render's **PostgreSQL** service.
- Update **Render environment variables** with the `.env` values.
- Use the following **startup command** in Render:

    ```sh
    python manage.py migrate && gunicorn loan_management.wsgi:application
    ```

## API Endpoints

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| POST   | `/api/register/`        | Register a new user          |
| POST   | `/api/verifyOtp/`       | Verify OTP                   |
| POST   | `/api/login/`           | User login                   |
| POST   | `/api/adminLogin/`      | Admin login                  |
| POST   | `/api/loanCreate/`      | Create a new loan            |
| GET    | `/api/loans/`           | Get loan details             |
| PATCH  | `/api/loanForeclose/`   | Foreclose a loan             |
| GET    | `/api/adminView/`       | View all loans in the system |
| GET    | `/api/adminUserView/`   | View all user loan details   |
| GET    | `/api/adminDeleteLoan/` | Delete loan records          |

## Troubleshooting

- **Database Connection Issues**: Ensure **DB_HOST** is set correctly (not `127.0.0.1` but Render's hostname).
- **Superuser Already Exists**: Reset password with `python manage.py changepassword admin`.
- **Email Not Sending**: Verify SMTP credentials and run `emailService.js`.

## Contact

For inquiries, reach out to [benjoybj891@gmail.com](mailto:benjoybj891@gmail.com) or visit the project repository on [GitHub](https://github.com/yourusername/loan-management-system).

---

This should now be in a more readable and presentable format.

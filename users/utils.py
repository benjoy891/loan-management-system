import datetime
import random
from django.conf import settings
import jwt
from .models import Loan, PaymentSchedule
import logging
from rest_framework.response import Response
import requests
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum



def generate_token(id):
    payload = {
        'user_id': id,
        'exp': datetime.utcnow() + datetime.timedelta(days=30)
    }
    jwt_token = jwt.encode(payload, 'secret', algorithm='HS256')
    return jwt_token

logger = logging.getLogger('django')


def error_response(message, status_code):
    response_data = {
        'status': "Failed",
        'message': message,
    }
    return Response(response_data, status=status_code)


def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp_email(email, otp):
    url = "https://email-service-4phn.onrender.com/send-otp"  
    payload = {"email": email, "otp": otp}
    
    try:
        response = requests.post(url, json=payload)
        return response.json()  # Return success/failure response
    except requests.exceptions.RequestException as e:
        print(f"Error sending OTP email: {e}")
        return {"success": False, "message": "Failed to send OTP"}


def calculate_monthly_installment(amount, tenure, interest_rate):
    """Calculates EMI using the formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)"""
    principal = amount
    rate = (interest_rate / 100) / 12  # Monthly interest rate
    months = tenure

    if rate == 0:
        return round(principal / months, 2)  # No interest case

    emi = principal * rate * ((1 + rate) ** months) / (((1 + rate) ** months) - 1)
    return round(emi, 2)

def calculate_total_interest(amount, tenure, interest_rate):
    """Calculates total interest payable over the loan tenure"""
    emi = calculate_monthly_installment(amount, tenure, interest_rate)
    return round((emi * tenure) - amount, 2)

def generate_payment_schedule(amount, tenure, interest_rate, start_date):
    """Generates the payment schedule with due dates"""
    emi = calculate_monthly_installment(amount, tenure, interest_rate)
    schedule = []

    for i in range(tenure):
        due_date = start_date + timedelta(days=(i + 1) * 30)  # Approximate 30-day month
        schedule.append({
            "installment_no": i + 1,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "amount": emi,
            "paid": False
        })

    return schedule


def calculate_foreclosure_amount(amount, tenure, interest_rate, start_date):
    completed_months = (date.today().year - start_date.year) * 12 + (date.today().month - start_date.month)
    remaining_months = tenure - completed_months
    if remaining_months <= 0:
        return Decimal(0)
    remaining_principal = amount * Decimal(remaining_months) / Decimal(tenure)
    foreclosure_fee = (remaining_principal * Decimal(interest_rate) / Decimal(100)) * Decimal(0.2)  
    return round(remaining_principal + foreclosure_fee, 2)

def calculate_foreclosure_discount(total_amount, tenure, interest_rate, start_date):
    completed_months = (date.today().year - start_date.year) * 12 + (date.today().month - start_date.month)
    remaining_months = tenure - completed_months
    if remaining_months <= 0:
        return Decimal(0)
    saved_interest = total_amount * (Decimal(interest_rate) / Decimal(100)) * (Decimal(remaining_months) / Decimal(12))  
    foreclosure_discount = saved_interest * Decimal(0.2)  
    return round(foreclosure_discount, 2)



def calculate_amount_remaining(loan: Loan) -> float:
    """Calculate the remaining loan balance."""
    return float(loan.amount + calculate_total_interest(loan.amount, loan.tenure, loan.interest_rate) - loan.amount_paid)

def get_next_due_date(loan: Loan) -> str:
    """Determine the next due date for the loan."""
    if loan.status == "ACTIVE":
        return loan.start_date.replace(day=24).isoformat()  # Assuming due every 24th
    return None


def update_loan_status(loan):
    paid_installments = PaymentSchedule.objects.filter(loan=loan, paid=True)
    add_total = paid_installments.aggregate(Sum("amount"))["amount__sum"] or 0    
    if loan.amount_paid is None:
        loan.amount_paid = 0
    loan.amount_paid += add_total
    loan.save()
    total_installments = PaymentSchedule.objects.filter(loan=loan).count()
    paid_installments_count = paid_installments.count()
    if total_installments > 0 and paid_installments_count == total_installments:
        loan.status = "CLOSED"
        loan.save()


def validate_loan_amount(amount):
    """Ensures the loan amount is within the allowed range (₹1,000 - ₹100,000)."""
    try:
        amount = float(amount)  # Ensure it's a number
    except (ValueError, TypeError):
        return error_response("Loan amount must be a valid number.", 400)

    if amount < 1000 or amount > 100000:
        return error_response("Loan amount must be between ₹1,000 and ₹100,000.", 400)

    return amount

def validate_loan_tenure(tenure):
    """Ensures the loan tenure is within the allowed range (3 to 24 months) and is a whole number."""
    try:
        tenure = int(tenure)  # Ensure it's a whole number
    except (ValueError, TypeError):
        return error_response("Tenure must be a whole number between 3 and 24 months.", 400)

    if tenure < 3 or tenure > 24:
        return error_response("Tenure must be between 3 and 24 months.", 400)

    return tenure
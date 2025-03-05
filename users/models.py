from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):  # pragma: no cover
        return f"{self.user.username} - OTP"


class Loan(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "ACTIVE"),
        ("CLOSED", "CLOSED"),
    ]
    loan_id = models.CharField(max_length=10, unique=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loans")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.PositiveIntegerField(help_text="Tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interest rate in percentage")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    start_date = models.DateField(auto_now_add=True, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    foreclosed_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Loan {self.loan_id} - {self.user.username} ({self.status})"


class PaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payment_schedules")
    installment_no = models.PositiveIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)


    def __str__(self):
        return f"Installment {self.installment_no} for Loan {self.loan.loan_id} - {self.loan.user.username}"

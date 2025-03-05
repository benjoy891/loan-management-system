from rest_framework import serializers
from .models import OTP, Loan, PaymentSchedule, User


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ('otp',)



class LoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ["loan_id", "amount", "tenure", "amount_paid", "total_amount", "interest_rate", "status", "created_at"] 

    def create(self, validated_data):
        latest_loan = Loan.objects.order_by("-loan_id").first()  
        if latest_loan and latest_loan.loan_id.startswith("LOAN"):
            latest_id = int(latest_loan.loan_id[4:]) 
            next_id = latest_id + 1
        else:
            next_id = 1  
        validated_data["loan_id"] = f"LOAN{next_id:03d}"  

        return super().create(validated_data)


class LoanOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["loan_id", "amount", "tenure", "amount_paid", "interest_rate",  "status", "created_at"]


class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = ["installment_no", "due_date", "amount", "paid"]
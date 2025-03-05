from itertools import count
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from rest_framework import status, generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from loan_management.messages import  ADMIN_ACCESS_REQUIRED_MESSAGE, EITHER_USERNAME_OR_EMAIL_REQ, EMAIL_ALREADY_PRESENT_MESSAGE, EXCEPTION_MESSAGE, FIRST_LAST_NAME_REQUIRED_MESSAGE, INVALID_INPUT_MESSAGE, LOGIN_SUCCESS_MESSAGE, NOT_ALLOWED_MESSAGE, NOT_VERIFIED_MESSAGE, OTP_VERIFICATION_INVALID_MESSAGE, OTP_VERIFICATION_SUCCESS_MESSAGE, REGISTRATION_SUCCESS, SENT_OTP_MESSAGE, USERNAME_ALREADY_PRESENT_MESSAGE
from users.serializers import LoanOutSerializer, LoanSerializer, OTPVerificationSerializer, PaymentScheduleSerializer, UserRegistrationSerializer
from .models import OTP, Loan, User, PaymentSchedule
from .utils import calculate_amount_remaining, generate_otp, generate_payment_schedule, get_next_due_date, logger, error_response, \
     send_otp_email, calculate_monthly_installment, calculate_total_interest, calculate_foreclosure_amount, calculate_foreclosure_discount, validate_loan_amount, validate_loan_tenure
from django.utils import timezone







class RegisterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]


    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if not serializer.is_valid():  
                return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)            
            username = serializer.validated_data.get("username")
            email = serializer.validated_data.get("email")
            first_name = serializer.validated_data.get("first_name")
            last_name = serializer.validated_data.get("last_name")

            if email and User.objects.filter(email=email).exists():
                url = request.build_absolute_uri()
                logger.error(f"URL: {url}, Exception: {EMAIL_ALREADY_PRESENT_MESSAGE}")
                return error_response(EMAIL_ALREADY_PRESENT_MESSAGE, status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                url = request.build_absolute_uri()
                logger.error(f"URL: {url}, Exception: {USERNAME_ALREADY_PRESENT_MESSAGE}")
                return error_response(USERNAME_ALREADY_PRESENT_MESSAGE, status.HTTP_400_BAD_REQUEST)  

            if not first_name or not last_name:
                url = request.build_absolute_uri()
                logger.error(f"URL: {url}, Exception: {FIRST_LAST_NAME_REQUIRED_MESSAGE}")
                return error_response(FIRST_LAST_NAME_REQUIRED_MESSAGE, status.HTTP_400_BAD_REQUEST)          

            user = serializer.save()
            if user.email:
                otp = generate_otp()
                OTP.objects.create(user=user, otp=otp)
                send_otp_email(email, otp)
            refresh = RefreshToken.for_user(user)

            response_data = {
                "status": "Success",
                "data": {
                    **serializer.data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "message": REGISTRATION_SUCCESS,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
                    
        except Exception as e:
            url = request.build_absolute_uri()
            logger.error(f"URL: {url}, Exception: {str(e)}")
            return error_response(EXCEPTION_MESSAGE, status.HTTP_400_BAD_REQUEST)

        



class OTPVerificationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = OTPVerificationSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                otp_value = serializer.validated_data.get('otp')
                latest_otp = OTP.objects.filter(user=user).order_by('-created_at').first()
                if latest_otp and latest_otp.otp == otp_value:
                    user.is_verified = True
                    user.save()
                    OTP.objects.filter(user=user).delete()
                    return Response({'result': True, 'message': OTP_VERIFICATION_SUCCESS_MESSAGE}, status=status.HTTP_200_OK)
                else:
                    url = self.request.build_absolute_uri()
                    logger.error(f"url: {url}, Exception: {OTP_VERIFICATION_INVALID_MESSAGE}")
                    return error_response(OTP_VERIFICATION_INVALID_MESSAGE, status.HTTP_400_BAD_REQUEST)
            else:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {INVALID_INPUT_MESSAGE}")
                return error_response(INVALID_INPUT_MESSAGE, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            url = self.request.build_absolute_uri()
            logger.error(f"url: {url}, Exception: {str(e)}")
            return error_response(EXCEPTION_MESSAGE, status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username_or_email = request.data.get("username") or request.data.get("email")
            if not username_or_email:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {EITHER_USERNAME_OR_EMAIL_REQ}")
                return error_response(EITHER_USERNAME_OR_EMAIL_REQ, status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(email=username_or_email).first() or User.objects.filter(username=username_or_email).first()
            if not user:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {INVALID_INPUT_MESSAGE}")
                return error_response(INVALID_INPUT_MESSAGE, status.HTTP_400_BAD_REQUEST)
            if not user.is_superuser:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {ADMIN_ACCESS_REQUIRED_MESSAGE}")
                return error_response(ADMIN_ACCESS_REQUIRED_MESSAGE, status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            refresh["role"] = "admin"
            response_data = {
                'status': "Success",
                'data': {
                    "username": user.username,
                    "email": user.email,
                    "role": "admin",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),                
                },
                'message': "Admin login successful."
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            url = request.build_absolute_uri()
            logger.error(f"URL: {url}, Exception: {str(e)}")
            return error_response("An error occurred while logging in.", status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username_or_email = request.data.get("username") or request.data.get("email")
            if not username_or_email:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {EITHER_USERNAME_OR_EMAIL_REQ}")
                return error_response(EITHER_USERNAME_OR_EMAIL_REQ, status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(email=username_or_email).first() or User.objects.filter(username=username_or_email).first()
            if not user:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {INVALID_INPUT_MESSAGE}")
                return error_response(INVALID_INPUT_MESSAGE, status.HTTP_400_BAD_REQUEST)
            if not user.is_verified:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {NOT_VERIFIED_MESSAGE}")
                return error_response(NOT_VERIFIED_MESSAGE, status.HTTP_400_BAD_REQUEST)
            if user.is_superuser:
                url = self.request.build_absolute_uri()
                logger.error(f"url: {url}, Exception: {NOT_ALLOWED_MESSAGE}")
                return error_response(NOT_ALLOWED_MESSAGE, status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            refresh["role"] = "user"
            response_data = {
                'status': "Success",
                'data': {
                    "username": user.username,
                    "email": user.email,
                    "role": "user",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),                
                },
                'message': "User login successful."
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            url = request.build_absolute_uri()
            logger.error(f"URL: {url}, Exception: {str(e)}")
            return error_response("An error occurred while logging in.", status.HTTP_400_BAD_REQUEST)



class LoanCreateView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        loan_amount = request.data.get("amount")
        loan_tenure = request.data.get("tenure")        
        validation_result = validate_loan_amount(loan_amount)
        if isinstance(validation_result, Response):  
            return validation_result    
        tenure_validation = validate_loan_tenure(loan_tenure)
        if isinstance(tenure_validation, Response):
            return tenure_validation      
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save(user=self.request.user)
        monthly_installment = calculate_monthly_installment(loan.amount, loan.tenure, loan.interest_rate)
        total_interest = calculate_total_interest(loan.amount, loan.tenure, loan.interest_rate)
        loan.total_interest = total_interest
        total_amount = loan.amount + total_interest
        loan.total_amount = total_amount
        loan.save()
        payment_schedule = generate_payment_schedule(loan.amount, loan.tenure, loan.interest_rate, loan.start_date)
        for installment in payment_schedule:
            PaymentSchedule.objects.create(
                loan=loan,
                installment_no=installment["installment_no"],
                due_date=installment["due_date"],
                amount=installment["amount"],
                paid=False,
            )
        response_data = {
            "status": "success",
            "data": {
                "loan_id": loan.loan_id,
                "amount": loan.amount,
                "tenure": loan.tenure,
                "interest_rate": f"{loan.interest_rate}% yearly",
                "monthly_installment": monthly_installment,
                "total_interest": loan.total_interest,
                "total_amount": loan.total_amount,
                "payment_schedule": payment_schedule,
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)    
    

class LoanListDetailView(generics.ListAPIView):
    serializer_class = LoanSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def get_object(self, loan_id):
        return get_object_or_404(Loan, loan_id=loan_id, user=self.request.user)

    def list(self, request, *args, **kwargs):
        loan_id = request.query_params.get("loan_id")
        if loan_id:
            loan = self.get_object(loan_id)
            payment_schedule = PaymentSchedule.objects.filter(loan=loan)
            payment_schedule_data = PaymentScheduleSerializer(payment_schedule, many=True).data
            remaining_balance = loan.total_amount - loan.amount_paid
            response_data = {
                "status": "success",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount": float(loan.amount),
                    "tenure": loan.tenure,
                    "interest_rate": f"{loan.interest_rate}% yearly",
                    "monthly_installment": calculate_monthly_installment(loan.amount, loan.tenure, loan.interest_rate),
                    "total_interest": loan.total_interest,
                    "total_amount": loan.total_amount,
                    "amount_paid": float(loan.amount_paid),
                    "remaining_balance": float(remaining_balance),
                    "start_date": loan.start_date.strftime("%Y-%m-%d"),
                    "status": loan.status,
                    "foreclosed_at": loan.foreclosed_at.strftime("%Y-%m-%d") if loan.foreclosed_at else None,
                    "created_at": loan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "payment_schedule": payment_schedule_data,
                }
            }
            return Response(response_data)
        queryset = self.get_queryset()
        active_loans = queryset.filter(status="ACTIVE")
        past_loans = queryset.filter(status="CLOSED")
        response_data = {
            "status": "success",
            "data": {
                "active_loans": [
                    {
                        **LoanOutSerializer(loan).data,
                        "total_amount": loan.amount + loan.total_interest,
                        "amount_remaining": calculate_amount_remaining(loan),
                        "next_due_date": get_next_due_date(loan),
                        "monthly_installment": calculate_monthly_installment(loan.amount, loan.tenure, loan.interest_rate),
                    }
                    for loan in active_loans
                ],
                "past_loans": [
                    {
                        **LoanOutSerializer(loan).data,
                        "total_amount": loan.amount + loan.total_interest,
                        "monthly_installment": calculate_monthly_installment(loan.amount, loan.tenure, loan.interest_rate),
                        "amount_paid": loan.amount + loan.total_interest - loan.amount_paid,
                    }
                    for loan in past_loans
                ],
            }
        }
        return Response(response_data)




class LoanForeclosureView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    authentication_classes = [JWTAuthentication]  
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        loan_id = request.data.get("loan_id")
        if not loan_id:
            return Response({"error": "loan_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        loan = get_object_or_404(Loan, loan_id=loan_id, user=request.user)
        if loan.status != "ACTIVE":
            return Response({"error": "Only active loans can be foreclosed."}, status=status.HTTP_400_BAD_REQUEST)
        foreclosure_discount = calculate_foreclosure_discount(loan.total_amount, loan.tenure, loan.interest_rate, loan.start_date)
        loan.status = "CLOSED"
        loan.foreclosed_at = timezone.now()
        loan.save()
        response_data = {
            "status": "success",
            "message": "Loan foreclosed successfully.",
            "data": {
                "loan_id": loan.loan_id,
                "amount_paid": float(loan.total_amount),
                "foreclosure_discount": float(foreclosure_discount),
                "final_settlement_amount": float(loan.total_amount - foreclosure_discount),
                "status": "CLOSED"
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)



class AdminLoanListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_role = request.auth.payload.get("role", "")
        if user_role != "admin":
            return Response({"error": "You do not have permission to view this data."}, status=403)
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)        
        return Response({"status": "success", "data": serializer.data}, status=200)


class AdminUserLoanListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_role = request.auth.payload.get("role", "")
        if user_role != "admin":
            return Response({"error": "You do not have permission to view this data."}, status=403)
        users = User.objects.filter(is_superuser=False)
        user_data = []
        for user in users:
            loans = Loan.objects.filter(user=user)
            loan_serializer = LoanSerializer(loans, many=True)
            user_data.append({
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_verified": user.is_verified
                },
                "loans": loan_serializer.data
            })
        return Response({"status": "success", "data": user_data}, status=200)



class AdminDeleteLoanView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user_role = request.auth.payload.get("role", "")
        if user_role != "admin":
            return Response({"error": "You do not have permission to delete loans."}, status=403)
        loan_id = request.data.get("loan_id")
        if not loan_id:
            return Response({"error": "loan_id is required."}, status=400)
        loan = get_object_or_404(Loan, loan_id=loan_id)
        loan.delete()
        return Response({"status": "success", "message": f"Loan {loan_id} deleted successfully."}, status=200)



def home_view(request):
    return JsonResponse({"message": "Welcome to Loan Management System API"})
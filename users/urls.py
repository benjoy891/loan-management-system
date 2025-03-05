from django.urls import path
from .views import RegisterView, OTPVerificationView, LoanListDetailView, LoanCreateView, LoanForeclosureView, \
                AdminLoanListView, AdminUserLoanListView, AdminDeleteLoanView, AdminLoginView, UserLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verifyOtp/', OTPVerificationView.as_view(), name='verifyOtp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('adminLogin/', AdminLoginView.as_view(), name='adminLogin'),
    path("loans/", LoanListDetailView.as_view(), name="loan-list"), 
    path("loanCreate/", LoanCreateView.as_view(), name="loan-create"), 
    path("loanForeclose/", LoanForeclosureView.as_view(), name="loan-foreclosure"),
    path("adminView/", AdminLoanListView.as_view(), name="admin-loan-view"),
    path("adminUserView/", AdminUserLoanListView.as_view(), name="admin-user-loan-view"),
    path("adminDeleteLoan/", AdminDeleteLoanView.as_view(), name="admin-delete-loan"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

from django.contrib import admin

# Register your models here.
from .models import User, Loan, PaymentSchedule


class UserAdmin(admin.ModelAdmin):
    list_display = ['username','first_name', 'last_name', 'email', 'is_staff']
    search_fields = ['first_name', 'last_name', ]
    list_per_page = 20


class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'user__username', 'amount', 'status']
    search_fields = ['user__username']
    list_per_page = 20


class PaymentSchedulesAdmin(admin.ModelAdmin):
    list_display = ['loan__loan_id', 'installment_no', 'due_date', 'amount', 'paid']
    search_fields = ['loan__loan_id', 'loan__user__username']
    list_per_page = 20




admin.site.register(User, UserAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(PaymentSchedule, PaymentSchedulesAdmin)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentSchedule, Loan
from django.db.models import Sum

@receiver(post_save, sender=PaymentSchedule)
def update_loan_amount_paid(sender, instance, **kwargs):

    if instance.paid:  
        loan = instance.loan

        loan.amount_paid = PaymentSchedule.objects.filter(loan=loan, paid=True).aggregate(Sum("amount"))["amount__sum"] or 0        
        total_installments = PaymentSchedule.objects.filter(loan=loan).count()
        paid_installments_count = PaymentSchedule.objects.filter(loan=loan, paid=True).count()
        if total_installments > 0 and paid_installments_count == total_installments:
            loan.status = "CLOSED"

        loan.save()  

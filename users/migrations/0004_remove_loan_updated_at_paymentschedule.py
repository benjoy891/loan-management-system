# Generated by Django 5.1.6 on 2025-03-03 03:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_loan_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='updated_at',
        ),
        migrations.CreateModel(
            name='PaymentSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('installment_no', models.PositiveIntegerField()),
                ('due_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid', models.BooleanField(default=False)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_schedules', to='users.loan')),
            ],
        ),
    ]

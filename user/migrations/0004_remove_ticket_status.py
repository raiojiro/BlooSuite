# Generated by Django 5.0.6 on 2024-06-12 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_ticket_status_ticket_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='status',
        ),
    ]

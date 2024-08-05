# Generated by Django 5.0.7 on 2024-08-05 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_alter_scholarshipprovider_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyscholarship',
            name='is_paid',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='applyscholarship',
            name='order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='applyscholarship',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='applyscholarship',
            name='payment_status',
            field=models.CharField(default='pending', max_length=20),
        ),
    ]

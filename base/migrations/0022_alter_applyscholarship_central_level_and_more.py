# Generated by Django 5.0.7 on 2024-08-02 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_alter_applyscholarship_central_level_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applyscholarship',
            name='central_level',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=40),
        ),
        migrations.AlterField(
            model_name='applyscholarship',
            name='college_level',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=40),
        ),
        migrations.AlterField(
            model_name='applyscholarship',
            name='state_level',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=40),
        ),
    ]

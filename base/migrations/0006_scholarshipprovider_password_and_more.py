# Generated by Django 5.0.7 on 2024-07-29 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_scholarshipprovider_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='scholarshipprovider',
            name='password',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='scholarshipprovider',
            name='provider_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
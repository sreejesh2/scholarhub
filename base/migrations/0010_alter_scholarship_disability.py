# Generated by Django 5.0.7 on 2024-07-29 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_scholarship_cast_scholarship_disability_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scholarship',
            name='disability',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('0', 'No')], max_length=200, null=True),
        ),
    ]

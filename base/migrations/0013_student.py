# Generated by Django 5.0.7 on 2024-07-30 08:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=100)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.scholarshipprovider')),
            ],
        ),
    ]

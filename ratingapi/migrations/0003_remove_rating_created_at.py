# Generated by Django 5.1.6 on 2025-03-08 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratingapi', '0002_alter_moduleinstance_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='created_at',
        ),
    ]

# Generated by Django 5.1.7 on 2025-05-20 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0002_add_jitsi_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='jitsi_room',
            field=models.CharField(blank=True, editable=False, max_length=50, verbose_name='Jitsi room'),
        ),
    ]

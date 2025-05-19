from django.db import migrations, models
import django.utils.timezone


def gen_default_room():
    return "TeamMeet_" + django.utils.timezone.now().strftime("%Y%m%d_%H%M%S")


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='jitsi_room',
            field=models.CharField(blank=True, editable=False, max_length=50, verbose_name='Jitsi room', default=gen_default_room),
        ),
    ]

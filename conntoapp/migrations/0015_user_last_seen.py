from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conntoapp', '0014_coursecenter_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Son Aktiflik'),
        ),
        migrations.AddField(
            model_name='coursecenter',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Son Aktiflik'),
        ),
    ]

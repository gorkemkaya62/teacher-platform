from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conntoapp', '0017_education_description_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='work_schedule',
            field=models.CharField(
                choices=[
                    ('tam_zamanli', 'Tam Zamanlı'),
                    ('yari_zamanli', 'Yarı Zamanlı'),
                    ('her_ikisi', 'Her İkisi İçin Uygun'),
                ],
                default='her_ikisi',
                max_length=20,
                verbose_name='Çalışma Şekli',
            ),
        ),
    ]

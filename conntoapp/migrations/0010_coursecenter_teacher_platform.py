# Generated manually for platform transformation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conntoapp', '0009_alter_company_options_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Company',
            new_name='CourseCenter',
        ),
        migrations.RenameField(
            model_name='coursecenter',
            old_name='company_name',
            new_name='center_name',
        ),
        migrations.RenameField(
            model_name='coursecenter',
            old_name='company_field',
            new_name='center_type',
        ),
        migrations.RenameField(
            model_name='coursecenter',
            old_name='employee_count',
            new_name='teacher_capacity',
        ),
        migrations.RenameField(
            model_name='userexperience',
            old_name='company_name',
            new_name='institution_name',
        ),
        migrations.AlterField(
            model_name='usereducation',
            name='degree',
            field=models.CharField(
                choices=[
                    ("Bachelor's Degree", "Bachelor's Degree"),
                    ("Master's Degree", "Master's Degree"),
                    ('Ph.D.', 'Ph.D.'),
                ],
                max_length=100,
                verbose_name='Derece',
            ),
        ),
        migrations.AlterField(
            model_name='usereducation',
            name='department',
            field=models.CharField(max_length=100, verbose_name='Bölüm'),
        ),
        migrations.AlterField(
            model_name='usereducation',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Bitiş'),
        ),
        migrations.AlterField(
            model_name='usereducation',
            name='school_name',
            field=models.CharField(max_length=100, verbose_name='Okul/Üniversite'),
        ),
        migrations.AlterField(
            model_name='usereducation',
            name='short_description',
            field=models.TextField(max_length=500, verbose_name='Açıklama'),
        ),
        migrations.AlterField(
            model_name='usereducation',
            name='start_date',
            field=models.DateField(verbose_name='Başlangıç'),
        ),
        migrations.AlterField(
            model_name='userexperience',
            name='department',
            field=models.CharField(max_length=100, verbose_name='Branş / Departman'),
        ),
        migrations.AlterField(
            model_name='userexperience',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Bitiş'),
        ),
        migrations.AlterField(
            model_name='userexperience',
            name='institution_name',
            field=models.CharField(max_length=100, verbose_name='Kurum / Kurs Merkezi Adı'),
        ),
        migrations.AlterField(
            model_name='userexperience',
            name='short_description',
            field=models.TextField(max_length=500, verbose_name='Açıklama'),
        ),
        migrations.AlterField(
            model_name='userexperience',
            name='start_date',
            field=models.DateField(verbose_name='Başlangıç'),
        ),
        migrations.AlterField(
            model_name='userservices',
            name='service_description',
            field=models.CharField(max_length=500, verbose_name='Açıklama'),
        ),
        migrations.AlterField(
            model_name='userservices',
            name='service_name',
            field=models.CharField(max_length=50, verbose_name='Ders/Branş Adı'),
        ),
        migrations.AlterField(
            model_name='userskill',
            name='skill_degree',
            field=models.SmallIntegerField(verbose_name='Seviye'),
        ),
        migrations.AlterField(
            model_name='userskill',
            name='skill_name',
            field=models.CharField(max_length=50, verbose_name='Yetkinlik'),
        ),
        migrations.AlterField(
            model_name='userawards',
            name='award_date',
            field=models.DateField(verbose_name='Tarih'),
        ),
        migrations.AlterField(
            model_name='userawards',
            name='award_name',
            field=models.CharField(max_length=30, verbose_name='Sertifika/Ödül Adı'),
        ),
        migrations.AlterModelOptions(
            name='userawards',
            options={'verbose_name': 'Sertifika', 'verbose_name_plural': 'Sertifikalar'},
        ),
        migrations.AlterModelOptions(
            name='usereducation',
            options={'verbose_name': 'Eğitim', 'verbose_name_plural': 'Eğitimler'},
        ),
        migrations.AlterModelOptions(
            name='userexperience',
            options={'verbose_name': 'Deneyim', 'verbose_name_plural': 'Deneyimler'},
        ),
        migrations.AlterModelOptions(
            name='userservices',
            options={'verbose_name': 'Verdiği Ders', 'verbose_name_plural': 'Verdiği Dersler'},
        ),
        migrations.AlterModelOptions(
            name='userskill',
            options={'verbose_name': 'Yetkinlik', 'verbose_name_plural': 'Yetkinlikler'},
        ),
    ]

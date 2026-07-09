from django.db import migrations, models


def migrate_userworks_fields(apps, schema_editor):
    UserWorks = apps.get_model('conntoapp', 'UserWorks')
    for work in UserWorks.objects.all():
        work.publisher_name = (
            getattr(work, 'work_service', None)
            or getattr(work, 'work_title', None)
            or 'Belirtilmemiş'
        )
        work.book_name = getattr(work, 'work_name', None) or 'Belirtilmemiş'
        work_year = getattr(work, 'work_year', None)
        work.publication_year = work_year.year if work_year else 2020
        work.save(update_fields=['publisher_name', 'book_name', 'publication_year'])


class Migration(migrations.Migration):

    dependencies = [
        ('conntoapp', '0011_increase_award_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='userworks',
            name='book_name',
            field=models.CharField(default='Belirtilmemiş', max_length=100, verbose_name='Kitap Adı'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userworks',
            name='publication_year',
            field=models.PositiveSmallIntegerField(default=2020, verbose_name='Yayın Yılı'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userworks',
            name='publisher_name',
            field=models.CharField(default='Belirtilmemiş', max_length=100, verbose_name='Yayınevi Adı'),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_userworks_fields, migrations.RunPython.noop),
        migrations.RemoveField(model_name='userworks', name='work_about'),
        migrations.RemoveField(model_name='userworks', name='work_description'),
        migrations.RemoveField(model_name='userworks', name='work_image1'),
        migrations.RemoveField(model_name='userworks', name='work_image2'),
        migrations.RemoveField(model_name='userworks', name='work_image3'),
        migrations.RemoveField(model_name='userworks', name='work_image4'),
        migrations.RemoveField(model_name='userworks', name='work_image5'),
        migrations.RemoveField(model_name='userworks', name='work_image6'),
        migrations.RemoveField(model_name='userworks', name='work_name'),
        migrations.RemoveField(model_name='userworks', name='work_service'),
        migrations.RemoveField(model_name='userworks', name='work_title'),
        migrations.RemoveField(model_name='userworks', name='work_year'),
    ]

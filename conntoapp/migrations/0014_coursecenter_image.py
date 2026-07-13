from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conntoapp', '0013_teacher_rating_favorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursecenter',
            name='image',
            field=models.ImageField(
                default='images/default.jpg',
                upload_to='course_centers/',
                verbose_name='Profil Fotoğrafı',
            ),
        ),
    ]

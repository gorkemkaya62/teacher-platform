from django.core.management.base import BaseCommand
from conntoapp.models import AdminUser

class Command(BaseCommand):
    help = 'İlk admin kullanıcısını oluşturur'

    def handle(self, *args, **options):
        if AdminUser.objects.exists():
            self.stdout.write(self.style.WARNING('Admin kullanıcısı zaten mevcut!'))
            return

        admin = AdminUser(
            username='admin',
            email='admin@ogretmenim.com'
        )
        admin.set_password('admin123')
        admin.save()

        self.stdout.write(self.style.SUCCESS('Admin kullanıcısı başarıyla oluşturuldu!')) 
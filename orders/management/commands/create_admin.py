from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Admin user yaratish'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@restaurant.uz',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Admin user yaratildi!')
            )
            self.stdout.write('Username: admin')
            self.stdout.write('Password: admin123')
        else:
            self.stdout.write('Admin user allaqachon mavjud!')
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username="admin").exists():
            return
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin",
            first_name="Nikita",
            last_name="Tuganov",
        )

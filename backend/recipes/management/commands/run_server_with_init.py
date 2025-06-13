import os
import subprocess
import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        init_script = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "init_db.py",
        )
        try:
            subprocess.run([sys.executable, init_script], check=True)
            self.stdout.write(self.style.SUCCESS("Запускаю сервер"))
            call_command("runserver", *args)
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Ошибка при инициализации базы данных: {str(e)}"
                )
            )
            sys.exit(1)

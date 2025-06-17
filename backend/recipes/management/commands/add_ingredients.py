import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "data",
            "ingredients.csv",
        )

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не найден!"))
            return

        count = 0

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)

                for row in csv_reader:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1]
                    )
                    count += 1

            self.stdout.write(
                self.style.SUCCESS(f"Успешно загружено {count} ингредиентов!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка: {str(e)}"))

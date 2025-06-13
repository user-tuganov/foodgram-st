import os
import subprocess
import sys
from pathlib import Path

import django


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True,
                                capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {command}")
        print(e.stderr, file=sys.stderr)
        sys.exit(1)


def create_superuser():
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@mail.com',
            password='admin',
            first_name='Niki',
            last_name='Niki'
        )
        print('Суперпользователь успешно создан!')
        print('Логин: admin')
        print('Пароль: admin')
        print('Email: admin@example.com')
    else:
        print('Суперпользователь уже существует')


def main():
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("Очищаю данные в бд")
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")

    print("Создаю и применяю миграции")
    run_command(f"{sys.executable} manage.py makemigrations")
    run_command(f"{sys.executable} manage.py migrate")

    print("Добавляю данные в бд")
    run_command(f"{sys.executable} manage.py add_ingredients")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
    django.setup()

    print("Создаю админа")
    create_superuser()

    print("Сервер запущен!")


if __name__ == "__main__":
    main()

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/Zorynix/foodgram.git
cd foodgram
```

### 2. Установка зависимостей для разработки
```bash
cd backend
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
```bash
# Создаем файл с переменными окружения в папке с env.example
```

## 📝 Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `SECRET_KEY` | Секретный ключ Django | `your-secret-key` |
| `DEBUG` | Режим отладки | `False` |
| `ALLOWED_HOSTS` | Разрешенные хосты | `localhost,127.0.0.1` |
| `DB_ENGINE` | Движок БД | `django.db.backends.postgresql` |
| `POSTGRES_DB` | Имя БД | `foodgram` |
| `POSTGRES_USER` | Пользователь БД | `foodgram_user` |
| `POSTGRES_PASSWORD` | Пароль БД | `your-password` |
| `DB_HOST` | Хост БД | `db` |
| `DB_PORT` | Порт БД | `5432` |

### 4. Запуск только бэкенда
```bash
# Униварсальной командой можем запустить автосоздание миграций, их применение
# Создается так же суперпользователь и подгружаются все инргредиенты
python3 manage.py run_server_with_init
```
```bash
# Если же требуется вручную что-то поменять, то примените сначала миграции:
python manage.py makemigrations
python manage.py migrate
# Загрузите ингредиенты:
python3 manage.py add_ingredients
# Создайте суперпользователя:
python manage.py createsuperuser
# Запустите сервер:
python manage.py runserver
```

### 5. Запуск всего приложения вместе
```bash
# Запустите docker-compose
docker-compose up
```
Приложение доступно (по умолчанию):
- localhost
- 127.0.0.1
Отдельно бэкенд доступен (по умолчанию):
- localhost:8000
Автор:
Туганов Никита

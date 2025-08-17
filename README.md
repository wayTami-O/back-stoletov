### Развёртка проекта (Django + PostgreSQL)

Короткое руководство для локального запуска и базовой подготовки к продакшену.

### Требования
- Python 3.13 (см. `Pipfile`)
- PostgreSQL 14+
- Опционально: pipenv (или используйте venv)

macOS (Homebrew):
```bash
brew install python@3.13 postgresql@14
brew services start postgresql@14
python3.13 -V && psql --version
```

### Переход в директорию проекта
```bash
cd /Users/brav1o/projects/start-app/back-stoletov
```

### Настройка PostgreSQL
Создайте базу и пользователя (пример — измените под себя):
```bash
createdb back_stoletov
psql -d postgres -c "CREATE USER back_user WITH PASSWORD 'back_password';"
psql -d postgres -c "ALTER ROLE back_user WITH LOGIN;"
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE back_stoletov TO back_user;"
```

### Переменные окружения
Создайте файл `.env` в корне проекта:
```bash
# Django
DJANGO_DEBUG=True
# SECRET_KEY=замените-на-секрет

# PostgreSQL
DB_NAME=back_stoletov
DB_USER=back_user
DB_PASSWORD=back_password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_CONN_MAX_AGE=60
# DB_SSLMODE=prefer

# Integrations (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
SOCIAL_ADMIN_TOKEN=
```
`config/settings.py` уже читает `.env` через `python-dotenv`.

### Установка зависимостей
Вариант A — pipenv (есть `Pipfile`):
```bash
pip install pipenv
pipenv install
```

Вариант B — venv:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install "psycopg[binary]" python-dotenv django
```

### Миграции и суперпользователь
```bash
# pipenv
pipenv run python manage.py migrate
pipenv run python manage.py createsuperuser

# venv/без pipenv
python manage.py migrate
python manage.py createsuperuser
```

### Запуск сервера разработки
```bash
# pipenv
pipenv run python manage.py runserver 0.0.0.0:8000

# venv/без pipenv
python manage.py runserver 0.0.0.0:8000
```
Откройте: http://127.0.0.1:8000/  Админка: http://127.0.0.1:8000/admin/

### Продакшен (минимум)
- `DEBUG=False`, задайте `SECRET_KEY` и переменные окружения
- Сборка статики:
```bash
pipenv run python manage.py collectstatic --noinput
# или
python manage.py collectstatic --noinput
```
- Настройте WSGI/ASGI (см. `config/wsgi.py`, `config/asgi.py`) и обратный прокси (nginx)

### Перенос данных из SQLite (опционально)
```bash
# До переключения на PostgreSQL
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude auth.permission --exclude contenttypes > data.json

# После миграций на PostgreSQL
python manage.py loaddata data.json
```

### Полезные команды
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

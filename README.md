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

---

## Развёртывание на сервере (Ubuntu/Debian + nginx)

### 1) Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3.13 python3.13-venv python3-pip nginx postgresql postgresql-contrib git

# Создание пользователя для приложения
sudo adduser --system --group --shell /bin/bash django
sudo usermod -aG sudo django
```

### 2) Настройка PostgreSQL
```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# В psql выполнить:
CREATE DATABASE back_stoletov;
CREATE USER django_user WITH PASSWORD 'your_strong_password';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE back_stoletov TO django_user;
\q
```

### 3) Клонирование и настройка проекта
```bash
# Переключение на пользователя django
sudo su - django

# Клонирование репозитория
git clone https://github.com/yourusername/back-stoletov.git
cd back-stoletov

# Создание виртуального окружения
python3.13 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -U pip
pip install "psycopg[binary]" python-dotenv django gunicorn

# Создание .env файла
cat > .env << EOF
# Django
DJANGO_DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# PostgreSQL
DB_NAME=back_stoletov
DB_USER=django_user
DB_PASSWORD=your_strong_password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_CONN_MAX_AGE=60

# Integrations (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
SOCIAL_ADMIN_TOKEN=
EOF

# Применение миграций
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4) Настройка Gunicorn
```bash
# Создание systemd сервиса
sudo tee /etc/systemd/system/django-back-stoletov.service > /dev/null << EOF
[Unit]
Description=Django Back Stoletov
After=network.target

[Service]
User=django
Group=django
WorkingDirectory=/home/django/back-stoletov
Environment="PATH=/home/django/back-stoletov/.venv/bin"
ExecStart=/home/django/back-stoletov/.venv/bin/gunicorn --workers 3 --bind unix:/home/django/back-stoletov/back_stoletov.sock config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl start django-back-stoletov
sudo systemctl enable django-back-stoletov
```

### 5) Настройка nginx
```bash
# Создание конфигурации nginx
sudo tee /etc/nginx/sites-available/back-stoletov > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/django/back-stoletov;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /home/django/back-stoletov;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/back-stoletov/back_stoletov.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активация сайта
sudo ln -s /etc/nginx/sites-available/back-stoletov /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6) Настройка SSL (Let's Encrypt)
```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автообновление сертификатов
sudo crontab -e
# Добавить строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7) Настройка файрвола
```bash
# UFW
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Или iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P INPUT DROP
```

### 8) Мониторинг и логи
```bash
# Проверка статуса сервисов
sudo systemctl status django-back-stoletov
sudo systemctl status nginx
sudo systemctl status postgresql

# Просмотр логов
sudo journalctl -u django-back-stoletov -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 9) Обновление кода
```bash
# Переключение на пользователя django
sudo su - django
cd back-stoletov

# Обновление кода
git pull origin main

# Активация окружения и обновление зависимостей
source .venv/bin/activate
pip install -r requirements.txt  # если есть requirements.txt

# Применение миграций и сбор статики
python manage.py migrate
python manage.py collectstatic --noinput

# Перезапуск сервиса
sudo systemctl restart django-back-stoletov
```

### 10) Резервное копирование
```bash
# Создание скрипта бэкапа
sudo tee /home/django/backup.sh > /dev/null << EOF
#!/bin/bash
BACKUP_DIR="/home/django/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Бэкап базы данных
sudo -u postgres pg_dump back_stoletov > \$BACKUP_DIR/db_\$DATE.sql

# Бэкап медиа файлов
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz /home/django/back-stoletov/media/

# Удаление старых бэкапов (старше 7 дней)
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

sudo chmod +x /home/django/backup.sh

# Добавление в cron (ежедневно в 2:00)
sudo crontab -e
# Добавить строку:
# 0 2 * * * /home/django/backup.sh
```

### 11) Переменные окружения для продакшена
Обязательно измените в `.env`:
- `SECRET_KEY` — сгенерируйте новый секретный ключ
- `DEBUG=False`
- `DB_PASSWORD` — используйте сильный пароль
- `ALLOWED_HOSTS` — добавьте ваш домен в `config/settings.py`

### 12) Полезные команды для управления
```bash
# Перезапуск всех сервисов
sudo systemctl restart django-back-stoletov nginx

# Проверка конфигурации nginx
sudo nginx -t

# Просмотр активных соединений
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Мониторинг ресурсов
htop
df -h
free -h
```

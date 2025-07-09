#!/bin/sh

echo "⏳ Ожидаем БД $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "✅ БД доступна. Применяем миграции и собираем статику..."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "🚀 Стартуем gunicorn…"
gunicorn tesseract_platform.wsgi:application \
  --bind 0.0.0.0:8001 \
  --timeout 120


FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "until python manage.py migrate; do echo 'Ожидание БД...'; sleep 2; done; python manage.py create_master_demo; python manage.py runserver 0.0.0.0:8000"]

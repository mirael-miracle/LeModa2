FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /store

ADD . /store

RUN pip install -r requirements.txt

COPY . .

# create user
RUN useradd -m -r appuser && chown appuser:appuser /store
USER appuser

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations --noinput && python manage.py migrate --noinput && echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'Qwe123ASD@@@ZXC1234') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')\" | python manage.py shell && gunicorn --bind 0.0.0.0:8000 store.wsgi:application"]
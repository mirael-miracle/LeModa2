FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /store

ADD . /store

RUN pip install -r requirements.txt

COPY . .

# create user
RUN useradd -m -r appuser && \
    mkdir -p /store/media && \
    chown -R appuser:appuser /store


RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "mkdir -p /store/media/product_images && chown -R appuser:appuser /store/media && chmod -R 755 /store/media && su appuser -c 'python manage.py makemigrations --noinput && python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 store.wsgi:application'"]
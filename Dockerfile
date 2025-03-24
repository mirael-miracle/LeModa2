FROM python:3.10

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /store

ADD . /store

RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "LeModa.wsgi:application"]

ENV C_FORCE_ROOT=true

CMD celery -A store worker -l info

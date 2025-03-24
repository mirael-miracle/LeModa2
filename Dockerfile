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

RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "store.wsgi:application"]

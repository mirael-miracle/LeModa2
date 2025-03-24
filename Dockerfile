FROM python:3.10

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /store

ADD . /store

RUN pip install -r requirements.txt

COPY . .

CMD ["sysctl", "vm.overcommit_memory=1"]

ENV C_FORCE_ROOT=true

CMD celery -A store worker -l info

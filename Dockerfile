FROM python:3.7-alpine
MAINTAINER haj-res

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/

COPY ./requirements.txt /app/
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/

RUN mkdir -p /var/www/media/
RUN mkdir -p /var/www/static/
RUN mkdir -p /code/logs/
RUN adduser -D user
RUN chown -R user:user /var/www/media/
RUN chown -R user:user /code/logs/
RUN chmod -R 777 /var/www/static/
RUN chmod -R 777 /code/logs/
COPY ./media/ /var/www/media/
USER user

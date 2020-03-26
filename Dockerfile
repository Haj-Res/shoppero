FROM python:3.7-alpine
MAINTAINER haj-res

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apk add --no-cache postgresql-client jpeg-dev \
 && apk add --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
 && pip install --upgrade pip \
 && pip install -r requirements.txt \
 && apk del .tmp-build-deps

COPY . /code/

RUN mkdir -p /var/www/media/ \
 && mkdir -p /var/www/static/ \
 && mkdir -p /code/logs/
RUN adduser -D user
RUN chown -R user:user /var/www/media/
RUN chown -R user:user /code/logs/
RUN chmod -R 777 /var/www/static/
RUN chmod -R 777 /code/logs/
COPY ./media/ /var/www/media/
USER user

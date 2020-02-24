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

RUN mkdir -p ./media
RUN mkdir -p ./static
RUN adduser -D user
RUN chown -R user:user ./media
RUN chmod -R 744 ./static
USER user

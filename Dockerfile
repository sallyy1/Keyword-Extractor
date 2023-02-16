FROM ubuntu:18.04
FROM python:3.9

MAINTAINER "hyunkyung_lee2@tmax.co.kr"

RUN apt-get -y update
RUN apt-get install software-properties-common -y
RUN apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main'
RUN apt-get -y update
RUN apt-get install g++ openjdk-8-jdk python3-dev python3-pip curl -y

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh | bash

EXPOSE 8887
CMD ["python","app.py"]
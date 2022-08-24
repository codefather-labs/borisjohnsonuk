FROM ubuntu:20.04 as ubuntu

USER root
ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

FROM python:3.10.5 as python3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/
WORKDIR /app/

RUN make linux_build
RUN python3 --version




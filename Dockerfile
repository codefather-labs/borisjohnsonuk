FROM ubuntu:20.04 as ubuntu

USER root

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Kiev

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get install -y python-dev python3-pip gcc g++ cmake clang python-dev nano \
    bpython3 postgresql libgmp10-dev build-essential libssl-dev libffi-dev ca-certificates mupdf libmupdf-dev \
    mupdf-tools python3-fitz
#RUN apt-get install -y tesseract-ocr-*

FROM python:3.10.5 as python3

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install setuptools cython fitz
RUN python3 -m pip install --upgrade pymupdf PyPDF2
#RUN python3 -m pip install --upgrade pytesseract

#COPY ./requirements.txt /requirements.txt
#RUN python3 -m pip install -r /requirements.txt
RUN python3 --version




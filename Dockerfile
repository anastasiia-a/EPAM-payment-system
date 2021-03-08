FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /payment_system
WORKDIR /payment_system

COPY ./requirements.txt /payment_system/
RUN pip install -r /payment_system/requirements.txt

COPY ./payment_system /payment_system

EXPOSE 8000
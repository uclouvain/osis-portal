FROM python:3.4
RUN apt-get update && apt-get upgrade -y && apt-get install gettext git -y
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
ADD requirements.txt /code/
ADD . /code/
WORKDIR /code
RUN git submodule update --init --recursive
RUN cp .env.example .env
RUN pip install -r requirements.txt

FROM python:3.4
RUN apt-get update && apt-get upgrade -y && apt-get install gettext git -y
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN mkdir /code/osis_common
WORKDIR /code
ADD requirements.txt /code/
RUN git submodule init && git submodule update
RUN cp .env.example .env
RUN pip install -r requirements.txt
ADD . /code/

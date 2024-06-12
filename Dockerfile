FROM python:3.9.18-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
    && apt install -y wget gettext postgresql-client \
    && mkdir -p /usr/src \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src
COPY . /usr/src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
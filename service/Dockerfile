FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /service

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --no-cache torch==2.3.1
RUN pip install --no-cache nvidia-cudnn-cu12==8.9.2.26
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg
RUN pip install --no-cache --upgrade -r requirements.txt

COPY ./ service
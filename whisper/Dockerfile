FROM python:3.12-slim

WORKDIR /whisper

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

# RUN pip install --no-cache torch==2.3.1
RUN pip install torch==2.3.1
# RUN pip install --no-cache nvidia-cudnn-cu12==8.9.2.26
RUN pip install nvidia-cudnn-cu12==8.9.2.26
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg
# RUN pip install --no-cache --upgrade -r requirements.txt

RUN apt-get update && apt-get install -y python3-distutils && python3 -c "import distutils; print('distutils installed')"

RUN pip install --upgrade -r requirements.txt

COPY ./ whisper

ARG WHISPER_PORT

CMD ["sh", "-c", "python toml_helper.py && uvicorn whisper.app.main:app --host 0.0.0.0 --port ${WHISPER_PORT} --reload"]
FROM python:3.10
# потому что в 3.10-slim нету gcc

WORKDIR /whisper

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN pip install --no-cache torch==2.3.1
RUN pip install torch==2.3.1
# RUN pip install --no-cache nvidia-cudnn-cu12==8.9.2.26
RUN pip install nvidia-cudnn-cu12==8.9.2.26
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg
# RUN pip install --no-cache --upgrade -r requirements.txt

COPY requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt

COPY ./ ./

CMD ["sh", "-c", "python app/toml_helper.py && python -m app.main.py"]
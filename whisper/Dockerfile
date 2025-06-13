# # Используем полный образ, потому что в 3.10-slim нету gcc
# FROM python:3.10 AS builder

# # директория сборки
# WORKDIR /install
# RUN apt-get update && apt-get install -y build-essential

# # сборка
# COPY requirements.txt requirements.txt
# RUN pip install --upgrade pip

# RUN apt-get install -y portaudio19-dev ffmpeg

# RUN pip wheel --no-deps --wheel-dir /wheels torch==2.3.1
# RUN pip wheel --no-deps --wheel-dir /wheels nvidia-cudnn-cu12==8.9.2.26
# RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

# FROM python:3.10

# # отключение генерации .pyc файлов
# ENV PYTHONDONTWRITEBYTECODE=1 
# # вывод сразу результатов без буферизации вывода
# ENV PYTHONUNBUFFERED=1

# # директория проекта
# WORKDIR /whisper

# COPY --from=builder /wheels /wheels

# COPY requirements.txt requirements.txt

# # скачиваем утилиту ffmpeg
# RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg

# # отдельно ставим тяжелые пакеты
# RUN pip install --no-deps --no-index --find-links=/wheels torch==2.3.1
# RUN pip install --no-deps --no-index --find-links=/wheels nvidia-cudnn-cu12==8.9.2.26
# # установка пакетов из уже собранных
# RUN pip install --no-deps --no-index --find-links=/wheels -r requirements.txt

# COPY ./ ./

# ENTRYPOINT ["sh", "-c"]
# CMD ["python app/toml_helper.py && python -m app.main"]


# +----------------------------------------------------------------------------------------------------------------------------+
# | REVIEW:                                                                  |
# | нихера не заработало, хотя собирается теперь очень быстро                                                                  |
# | проблема видимо в том, что разделение на builder-стадию вызывает конфликт или отсутствие правильной установки зависимостей |
# +----------------------------------------------------------------------------------------------------------------------------+

FROM python:3.10
# Используем полный образ, потому что в 3.10-slim нету gcc

WORKDIR /whisper

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install torch==2.3.1
RUN pip install nvidia-cudnn-cu12==8.9.2.26
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg

COPY requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt

COPY ./ ./

CMD ["sh", "-c", "python app/toml_helper.py && python -m app.main"]
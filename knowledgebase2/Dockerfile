FROM python:3.12-slim AS builder

# директория сборки
WORKDIR /install
RUN apt-get update && apt-get install -y build-essential

# сборка
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim

# отключение генерации .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1 
# вывод сразу результатов без буферизации вывода
ENV PYTHONUNBUFFERED=1

# директория проекта
WORKDIR /knowledgebase2

COPY --from=builder /wheels /wheels

COPY requirements.txt requirements.txt

# установка пакетов из уже собранных
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY ./ ./

ARG KNOWLEDGEBASE_PORT
ENV KNOWLEDGEBASE_PORT=${KNOWLEDGEBASE_PORT}

ENTRYPOINT ["sh", "-c"]
CMD ["python app/toml_helper.py && uvicorn app.main:app --host 0.0.0.0 --port ${KNOWLEDGEBASE_PORT} --reload"]

FROM python:3.12-slim

WORKDIR /core

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade -r requirements.txt

COPY ./ ./

ARG CORE_PORT
ENV CORE_PORT=${CORE_PORT}

CMD ["sh", "-c", "python app/toml_helper.py && uvicorn app.main:app --host 0.0.0.0 --port ${CORE_PORT} --reload"]

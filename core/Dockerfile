FROM python:3.12-slim

WORKDIR /core

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade -r requirements.txt

COPY ./ core

ARG CORE_PORT

CMD ["sh", "-c", "python toml_helper.py && uvicorn core.app.main:app --host 0.0.0.0 --port ${CORE_PORT} --reload"]

FROM python:3.12-slim

WORKDIR /knowledgebase2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade -r requirements.txt

COPY ./ ./

ARG KNOWLEDGEBASE_PORT
ENV KNOWLEDGEBASE_PORT=${KNOWLEDGEBASE_PORT}

CMD ["sh", "-c", "python app/toml_helper.py && uvicorn app.main:app --host 0.0.0.0 --port ${KNOWLEDGEBASE_PORT} --reload"]

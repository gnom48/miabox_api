FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /knowledgebase

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ARG KNOWLEDGEBASE_PORT
ENV KNOWLEDGEBASE_PORT=${KNOWLEDGEBASE_PORT}

ARG LOG_LEVEL
ENV LOG_LEVEL=${LOG_LEVEL}

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${KNOWLEDGEBASE_PORT} -w 3 --log-file - --log-level debug --access-logfile - app.app:app"]
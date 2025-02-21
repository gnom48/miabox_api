FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /knowledgebase

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG KNOWLEDGEBASE_PORT
ARG LOG_LEVEL

CMD ["gunicorn", "-b", "0.0.0.0:${KNOWLEDGEBASE_PORT}", "-w", "3", "--log-file", "-", "--log-level", "debug", "--access-logfile", "-", "app.app:app"]
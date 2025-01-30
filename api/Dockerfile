FROM python:3.12-slim

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade -r requirements.txt

COPY ./ api

EXPOSE 8082

CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8082", "--reload"]
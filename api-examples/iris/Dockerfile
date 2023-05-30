FROM python:3.9.16-slim

RUN mkdir /app
WORKDIR /app
ADD api-examples/iris/ /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    rm poetry.lock pyproject.toml

EXPOSE 9000

CMD uvicorn run:app --host 0.0.0.0 --port 9000 --workers 5
FROM python:3.8.2-alpine

WORKDIR /code

COPY ./requirements /code/requirements

RUN pip install --no-cache-dir --upgrade -r /code/requirements/base.txt && \
    pip install --no-cache-dir --upgrade -r /code/requirements/deployment.txt

COPY ./app /code/app
COPY ./*.env /code/

CMD ["uvicorn", "app.v1:app", "--host", "0.0.0.0", "--port", "8000"]

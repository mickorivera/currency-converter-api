# currency-converter-api
This repository contains API endpoints used to convert currencies.

This application is tested to run in Python 3.8.

Currencies supported depends on this [External Currency Exchange](https://exchangerate.host/#/docs).

## Local Machine Setup
To be updated

```shell
export ENV=dev
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements/base.txt
pip install -r requirements/deployment.txt
uvicorn app.v1:app --reload
```

Once the server is up and running, you can visit the [swagger documentation](http://127.0.0.1:8000/v1).


## Unit Test
```shell
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements/test.txt
pytest --cov=. tests/
```

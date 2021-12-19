# currency-converter-api
This repository contains API endpoints used to convert currencies.

This application is tested to run in Python 3.8.

Currencies supported depends on this [External Currency Exchange](https://exchangerate.host/#/docs).

## Local Machine Setup
```shell
# build docker image
docker build . -t api/currency-conversion

# run docker container
docker run -it -p 8000:8000 --rm --env ENV=dev api/currency-conversion
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

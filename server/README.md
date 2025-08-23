# CVision-API

## RESTful API implementation for CVision using FastAPI -->

## Using the applicaiton

To use the application, follow the outlined steps:

1. Clone this repository and create a virtual environment in it:
```console
git clone https://github.com/C-Senanayake/CVision.git
```

2. goto server directory.

```console
cd server
```

3. Create a python virtual environment and activate it

```console
$ python -m venv venv
```

```console
$ ./venv/Scripts/activate
```

5. Install the modules listed in the `requirements.txt` file:

```console
(venv)$ pip install -r requirements.txt
```

6. You also need to start your mongodb instance. See the `.env.sample` for configurations.

7. goto src directory.

```console
cd src
```

8. Start the application:

```console
python run.py
```

The starter listens on port 8000 on localhost

## License

This project is licensed under the terms of MIT license.
### Load Testing Framework (Built Using [Locust](https://locust.io/))

Create a virtualenv: `python3 -m venv venv`

Activate virtual env: `. ./venv/bin/activate`

Install: `pip install -r requirements.txt`

Run the application:  `python3 api.py`

Will need to include a config.ini file with the following:
```
[mysql]
host = 
port = 
user = 
pass = 
database = 
```
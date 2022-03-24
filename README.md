### WIP: New Zealand Gas Emissions API

Work in progress.  This project is to illustrate an application programming interface (API) developed using Python + the Flask micro web framework.  The API fetches data from a MySQL database that is hosted on AWS RDS.  Additionally, this API can be containerized with the associated Dockerfile in the project repo.

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

To run as a Docker container, execute the following commands on the project root directory:
```
docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -f Dockerfile -t some-image-name .
docker run -d -p 5000:5000 some-image-name --name some-container-name
```
Service can be accessed at http://my.web.host.com:5000

### Technologies/Languages
* Application
    * Python
    * Flask
    * Docker
* AWS
    * ECS
    * RDS 
    * API Gateway
* CI/CD
    * GitHub Actions
    * Terraform
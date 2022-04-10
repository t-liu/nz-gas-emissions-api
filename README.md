## WIP: New Zealand Gas Emissions API

Work in progress.  This project is to illustrate an application programming interface (API) developed using Python + the Flask micro web framework.  The API fetches data from a MySQL database that is hosted on AWS RDS.  Additionally, this API can be containerized with the associated Dockerfile in the project repo.  Entire infrastructure, including VPC components + load balancer + DNS routing, can be deployed via Hashicorp Terraform.

### Run in Python

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

### Containerize the API

To run as a Docker container, execute the following commands on the project root directory:
```
docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -f Dockerfile -t some-image-name .
docker run -d -p 5000:5000 some-image-name
```
When running locally, service can be accessed at http://localhost:5000/emissions

### Terraform Setup

Initiate, plan, and apply the Terraform workspace:

```sh
terraform init
terraform plan -var-file="./tf/vars/secrets.tfvars" -var-file="./tf/vars/environment.tfvars"
terraform apply -var-file="./tf/vars/secrets.tfvars" -var-file="./tf/vars/environment.tfvars"
```
To destroy the Terraform workspace:

```sh
terraform plan -destroy -var-file="./tf/vars/secrets.tfvars" -var-file="./tf/vars/environment.tfvars"
terraform apply -var-file="./tf/vars/secrets.tfvars" -var-file="./tf/vars/environment.tfvars"
```

### Technologies/Languages
* Application
    * Python
    * Flask
    * Docker
* AWS
    * VPC
    * RDS 
    * ALB
    * SSM
    * ECS
    * Route 53
    * API Gateway
* CI/CD
    * GitHub Actions
    * Terraform

### Items to still work on
* Pagination for API
* DB connection pooling
* Maybe a circuit breaker
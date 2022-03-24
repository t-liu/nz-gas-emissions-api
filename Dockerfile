FROM alpine:latest

MAINTAINER Thomas Liu "thomas.s.liu@gmail.com"

USER root

RUN apk update && apk add --no-cache git openssh py3-pip python3
# install -y --no-install-recommends

RUN pip install --upgrade pip

# add credentials on build
# run the following to build locally:
# docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" -t nora-media-service .
ARG SSH_PRIVATE_KEY
RUN mkdir /root/.ssh/ && \
    echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa && \
    touch /root/.ssh/known_hosts && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

# copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "api.py" ]
FROM python:3.7

# author info
LABEL maintainer="Pablo Luque <pabloluque13@gmail.com>"

# Working directory 
WORKDIR /

# copy dependencies file
COPY requirements.txt ./

# copy forecast models
COPY /tmp/workflow/arimaTemp.pkl ./
COPY /tmp/workflow/arimaHum.pkl ./

# copy microservice file
COPY microservice_v1.py ./

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# up the service
CMD gunicorn --bind 0.0.0.0:5000 microservice_v1:app
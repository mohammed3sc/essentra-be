FROM python:3.10

# setup environment variable
ENV DOCKERHOME=/home/Essentra_BE
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install vim and netools
RUN apt-get update -y && apt-get install -y vim net-tools

# set work directory  
RUN mkdir -p $DOCKERHOME

# install dependencies  
RUN pip install --upgrade pip

# copy whole project to your docker home directory. 
COPY . $DOCKERHOME/

# where your code lives
WORKDIR $DOCKERHOME

# run this command to install all dependencies
RUN pip install -r requirements.txt

# update the dockerhome env
ENV DOCKERHOME=/home/Essentra_BE

# where your code lives
WORKDIR $DOCKERHOME

# port where the Django app runs
EXPOSE 8000

# start server
CMD python manage.py makemigrations || true && python manage.py migrate || true && python manage.py runserver 0:8000 && python consumer.py && python producer.py

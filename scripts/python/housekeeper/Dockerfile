FROM python:3.9-buster
LABEL maintainer="Asdrubal Gonzalez Penton<asdrubal.gonzalez@geo-solutions.it>"

WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip3 install -r requirements.txt

COPY housekeeper.py /code/housekeeper.py

CMD ["python3", "housekeeper.py"]

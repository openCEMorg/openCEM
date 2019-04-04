FROM python:3

WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get upgrade -y tzdata \
  && apt-get install -y coinor-cbc

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "pytest" ]

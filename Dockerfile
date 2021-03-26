# Miniconda with Python 3
FROM continuumio/miniconda3:4.8.2

# build new locales
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN sed -i -e 's/# en_AU.UTF-8 UTF-8/en_AU.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_AU.UTF-8
ENV LANGUAGE en_AU:en
ENV LC_ALL en_AU.UTF-8

# Install solver
RUN conda install -y -c conda-forge coincbc

# Set working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

ADD requirements.txt .

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

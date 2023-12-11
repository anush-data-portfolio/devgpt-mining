# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends --yes build-essential && \
    pip install pipenv && \
    pip install "dask[distributed]" --upgrade

# Copy the Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/  

# Install dependencies using pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . .

RUN apt-get install curl -y
RUN apt-get install unzip -y

RUN mkdir data
RUN curl -LJO https://zenodo.org/records/10086809/files/DevGPT.zip?download=1 && unzip -o DevGPT.zip -d data && rm DevGPT.zip

RUN mkdir model
# install lid.176.bin from https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin in the app directory
RUN curl -LJO https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin  && mv lid.176.bin model/lid.176.bin


# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Initialize SQLite database
RUN touch devgpt.sqlite

# Expose the port the app runs on
EXPOSE 8786

# Define environment variable
ENV DASK_SCHEDULER_ADDRESS tcp://scheduler:8786




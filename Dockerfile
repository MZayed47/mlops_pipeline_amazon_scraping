# Use official Python image from the DockerHub
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY ./requirements.txt /app/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy everything to the container
# COPY . .
COPY ./amazon_watches_v2.py /app/amazon_watches_v2.py
COPY ./api_v1.py /app/api_v1.py
COPY ./utility_v1.py /app/utility_v1.py

# Add folders as data mount points
ADD data /code/data/
# ADD cred /code/cred/

# Use the official Python image as a base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /tubescript_backend

# Copy the requirements.txt into the container
COPY requirements.txt /tubescript_backend/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /tubescript_backend

# Expose the port your backend server runs on
EXPOSE 8080

# Define the command to run your backend server
CMD ["python", "main.py"]

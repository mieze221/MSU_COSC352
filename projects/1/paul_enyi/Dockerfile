# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /appdocker info

# Copy the script into the container's working directory
COPY Hello_Paul.py /app/.

# Define the command to run the script with arguments
ENTRYPOINT ["python", "/app/Hello_Paul.py"]

# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required dependencies, including lxml
RUN pip install --no-cache-dir requests beautifulsoup4 pandas lxml

# Command to run your Python script
CMD ["python", "extract_tables.py"]

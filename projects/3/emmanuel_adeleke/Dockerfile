# Use the official Crystal Docker image as the base
FROM crystallang/crystal:latest

# Set the working directory in the container to /app
WORKDIR /app

# Install required dependencies for the project
RUN apt-get update && apt-get install -y \
  curl \
  build-essential \
  libssl-dev \
  libyaml-dev \
  zlib1g-dev

# Copy the entire project into the container
COPY . /app

# Install dependencies (if using shards)
RUN shards install

# Build the Crystal application (if required)
RUN crystal build hello.cr --release

# Command to run the Crystal program when the container starts
CMD ["./hello"]

# Expose any necessary ports (optional, depending on your application)
EXPOSE 8080

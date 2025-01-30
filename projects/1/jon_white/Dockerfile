# Use a lightweight base image
FROM alpine:latest

# Install bash
RUN apk add --no-cache bash

# Set the working directory
WORKDIR /app

# Copy the script into the container
COPY hello.sh /app/hello.sh

# Ensure correct line endings
RUN sed -i 's/\r$//' /app/hello.sh && chmod +x /app/hello.sh

# Set the default command to run the script
ENTRYPOINT ["/bin/bash", "/app/hello.sh"]

# Use the official Nim base image
FROM nimlang/nim:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the Nim source code into the container
COPY hello.nim .

# Compile the Nim source code
RUN nim compile --verbosity:0 --compileOnly hello.nim

# Run the compiled program
ENTRYPOINT ["./hello"]

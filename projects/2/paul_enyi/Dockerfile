# Use the official Haskell image
FROM haskell:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the Haskell script into the container
COPY Haskell-project2.hs .

# Install necessary Haskell tools
RUN apt-get update && apt-get install -y ghc cabal-install

# Ensure runghc is in PATH
ENV PATH="/root/.ghcup/bin:${PATH}"

# Set the default command to run the script
ENTRYPOINT ["runhaskell", "Haskell-project2.hs"]

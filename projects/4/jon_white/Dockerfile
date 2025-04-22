FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy script into container
COPY parse_tables.py /app/

# Ensure script is executable
RUN chmod +x /app/parse_tables.py

# Install any required system dependencies (if needed)
# No additional Python packages required; using standard library

# Default entrypoint: run the parser script
ENTRYPOINT ["python", "parse_tables.py"]

# Example command: pass comma-separated URLs as arguments to Docker run
# Usage:
#   docker build -t table-parser .
#   docker run --rm table-parser "https://example.com/page1,https://example.com/page2"

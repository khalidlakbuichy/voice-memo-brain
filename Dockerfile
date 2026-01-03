# Use lightweight Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some audio operations)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
# Copy credentials (WARNING: Only for local build, in production use Secrets)
# For a portfolio demo, we usually mount these as volumes, but for simplicity:
# COPY credentials.json . 

# Command to run the bot
CMD ["python", "src/main.py"]
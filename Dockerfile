# Use Python 3.11 lightweight Linux environment
FROM python:3.11-slim

# Install system dependencies (required for ocrmypdf)
RUN apt-get update && apt-get install -y \
    ocrmypdf \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python packages first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run the main script on startup
CMD ["python", "main.py"]
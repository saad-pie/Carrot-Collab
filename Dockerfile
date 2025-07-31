FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements_arm64.txt .

# Install Python dependencies
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements_arm64.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
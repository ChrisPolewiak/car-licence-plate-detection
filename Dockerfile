FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python", "plate_detection.py"]
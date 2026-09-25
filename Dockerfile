FROM python:3.10-slim

WORKDIR /app

# Install system dependencies yang dibutuhkan OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install PyTorch dan Ultralytics versi terbaru yang mendukung model C3k2
RUN pip install --no-cache-dir "torch<2.6.0" "torchvision<2.6.0"
RUN pip install --no-cache-dir ultralytics>=8.3.0
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]

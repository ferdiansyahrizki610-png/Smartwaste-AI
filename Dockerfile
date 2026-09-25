FROM python:3.10-slim

WORKDIR /app

# Install system dependencies yang dibutuhkan OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instal dependensi utama dengan versi yang kompatibel secara langsung
RUN pip install --no-cache-dir "numpy<2.0.0"
RUN pip install --no-cache-dir "torch<2.6.0" "torchvision<2.6.0"
RUN pip install --no-cache-dir ultralytics>=8.3.0
RUN pip install --no-cache-dir Flask==3.0.2 werkzeug==3.0.1 opencv-python-headless==4.9.0.80

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]

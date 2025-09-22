FROM python:3.12-slim

# Install system dependencies required by matplotlib and common networking
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpng-dev \
       libfreetype6-dev \
       libjpeg-dev \
       libblas3 \
       liblapack3 \
       gcc \
       pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Default data files (can be mounted as volumes)
VOLUME ["/app/data"]

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "bpi_collector.py"]

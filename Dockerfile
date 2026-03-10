FROM python:3.11-slim

WORKDIR /app

# System deps for Playwright + curl_cffi
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (only if needed)
# RUN playwright install chromium && playwright install-deps

COPY . .

CMD ["python", "cli.py"]

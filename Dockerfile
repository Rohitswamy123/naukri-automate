FROM python:3.11-slim

# System dependencies for Chromium + Xvfb on Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    wget \
    ca-certificates \
    fonts-liberation \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's Chromium browser
RUN playwright install chromium

COPY naukri_bot/ ./naukri_bot/
COPY main.py .

# Session file persists via mounted volume (see docker-compose.yml)
VOLUME ["/app/data"]

ENV SESSION_FILE=/app/data/naukri_session.json

CMD ["python", "-u", "main.py"]

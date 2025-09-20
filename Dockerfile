FROM python:3.10-slim

WORKDIR /app

# 安裝必要的系統依賴與 Google Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl fonts-liberation gnupg2 libcups2 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libdrm2 libgbm1 libgl1 libglib2.0-0 \
    libnss3 libnspr4 libpangocairo-1.0-0 libx11-6 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxshmfence1 \
    libxcb1 unzip wget \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 相依套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]

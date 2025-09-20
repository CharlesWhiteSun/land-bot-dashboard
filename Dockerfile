FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxdamage1 libxrandr2 libxrender1 libgbm1 \
    libasound2 libpangocairo-1.0-0 libdrm2 libx11-6 libx11-xcb1 \
    libxfixes3 libxext6 unzip wget libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright

RUN playwright install
RUN playwright install-deps

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]

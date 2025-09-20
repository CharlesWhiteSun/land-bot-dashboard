FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxkbcommon0 libx11-6 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libxrender1 libxfixes3 libgbm1 libasound2 libcups2 \
    libatk1.0-0 libatk-bridge2.0-0 libpangocairo-1.0-0 libdrm2 \
    libnss3 libxext6 unzip wget libxcursor1 libgtk-3-0 \
    libgdk-pixbuf-xlib-2.0-0 libcairo2 libcairo-gobject2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright

RUN playwright install
RUN playwright install-deps

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]

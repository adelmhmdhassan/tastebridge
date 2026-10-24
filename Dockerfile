# TasteBridge — all-in-one image: FastAPI (Python 3.12) + qloo harness CLI (Node 20)
FROM python:3.12-slim

# 1. Install Node.js (required by the qloo CLI)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# 2. Install the Qloo harness CLI globally
RUN npm install -g @qloo/qloo-harness@0.1.26

# 3. Trust the hackathon endpoint inside the image (base URL is not a secret)
RUN qloo config set base-url https://hackathon.api.qloo.com

# 4. Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. App code
COPY . .

# QLOO_API_KEY is provided by Render env vars (never baked into the image)
ENV QLOO_MODE=harness
ENV QLOO_TRUSTED_BASE_URL=https://hackathon.api.qloo.com

CMD uvicorn main:app --host 0.0.0.0 --port $PORT

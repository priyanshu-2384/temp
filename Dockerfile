# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for headless Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    build-essential \
    libnss3 \
    libatk1.0-0 \
    libgconf-2-4 \
    libx11-xcb1 \
    libcups2 \
    libxrandr2 \
    libasound2 \
    libxtst6 \
    libxss1 \
    libappindicator3-1 \
    libnspr4 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libdbus-1-3 \
    libatspi2.0-0 \
    xdg-utils \
    && apt-get clean

# Download and install Stable Chromium (131.0.6778.204)
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chrome-linux64.zip" && \
    unzip chrome-linux64.zip && \
    mv chrome-linux64 /usr/local/chrome && \
    ln -s /usr/local/chrome/chrome /usr/bin/google-chrome-stable && \
    rm -f chrome-linux64.zip

# Download and install matching ChromeDriver (131.0.6778.204)
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64 /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -f chromedriver-linux64.zip

# Set environment variables for Chrome
ENV PATH="/usr/local/chrome:${PATH}"

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Expose the port for Flask
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application (use Gunicorn in production)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "app:app"]



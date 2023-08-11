# Use an official Python runtime as the parent image
FROM python:3.11.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc libpq-dev &&  \
    apt-get install -y wget unzip && \
    apt-get clean &&  \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY .. ./
RUN pip install --upgrade pip
## Install required Python libraries
RUN pip install -r requirements.txt

# Install Google Chrome
RUN apt-get update && apt-get install -y wget gnupg2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Specify the command to run on container start

CMD ["bash", "run.sh"]

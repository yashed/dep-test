# Use an official Python image as the base image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /apps/geronimo/app

# Install required system dependencies for Selenium & Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_DRIVER_BIN=/usr/bin/chromedriver

# Copy the requirements file first for better caching
COPY requirements.txt /apps/geronimo/

# Install Python dependencies
RUN pip install --no-cache-dir -r /apps/geronimo/requirements.txt && \
    pip install --no-cache-dir selenium webdriver-manager

# Copy the entire application code
COPY . /apps/geronimo/

# Create a new user with UID 10016 for security
RUN addgroup --gid 10016 choreo && \
    adduser --disabled-password --no-create-home --uid 10016 --ingroup choreo choreouser && \
    chown -R 10016:10016 /apps/geronimo

# Switch to the unprivileged user
USER 10016

# Ensure the correct user is in effect
RUN whoami && id

# Expose the FastAPI port (8000)
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

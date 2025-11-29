# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# gcc is often needed for compiling python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Convert entrypoint.sh to Unix line endings
RUN dos2unix entrypoint.sh

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER root
RUN chmod +x entrypoint.sh
USER appuser

# Expose port 5000 to the outside world
EXPOSE 5000

# Run the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

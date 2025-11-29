#!/bin/sh

# Create the instance directory if it doesn't exist
# This is where the SQLite database usually lives
mkdir -p instance

# Start the Gunicorn server
# -w 4: uses 4 worker processes (good for handling multiple requests)
# -b 0.0.0.0:5000: binds to all network interfaces on port 5000
# --access-logfile - : logs to stdout
# --error-logfile - : logs errors to stderr
# app:app : refers to the 'app' object in 'app.py'
exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app

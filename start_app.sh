#!/bin/bash

# Define the paths to your virtual environment and Flask app
VENV_PATH="~/privacy-scanner/venv"  # Path to your virtual environment
APP_PATH="~/privacy-scanner/app.py"  # Path to your Flask app
LOG_PATH="~/privacy-scanner/logs/flask_app.log"  # Path to your log file (ensure the logs folder exists)

# Expand the tilde (~) to the full path
VENV_PATH=$(eval echo $VENV_PATH)
APP_PATH=$(eval echo $APP_PATH)
LOG_PATH=$(eval echo $LOG_PATH)

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
  echo "Error: Virtual environment not found at $VENV_PATH"
  exit 1
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Check if the Flask app exists
if [ ! -f "$APP_PATH" ]; then
  echo "Error: Flask app not found at $APP_PATH"
  deactivate
  exit 1
fi

# Run the Flask app and log output to a file
echo "Starting Flask app..."
nohup python "$APP_PATH" > "$LOG_PATH" 2>&1 &

# Check if the app started successfully
if [ $? -eq 0 ]; then
  echo "Flask app started successfully. Logs can be found at $LOG_PATH."
else
  echo "Error: Failed to start Flask app."
  deactivate
  exit 1
fi

# Deactivate virtual environment
deactivate

#!/bin/bash

# Load environment variables if needed (though Docker envs are usually sufficient)
# printenv > /etc/environment

# Start cron service in the background
service cron start

# Ensure the log file exists
touch /var/log/cron.log

# Start the application
# Using exec to replace the shell process with uvicorn, so signals are passed correctly
exec uvicorn server:app --host 0.0.0.0 --port 8000

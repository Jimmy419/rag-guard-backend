#!/bin/bash
# Remove all files in the charts directory
# Suppress error if directory is empty or doesn't exist yet
rm -f /app/static/charts/*
echo "$(date): Cleaned up src/static/charts" >> /var/log/cron.log

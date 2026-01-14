FROM python:3.11-slim

# Install system dependencies
# cron: for scheduled tasks
# fonts-noto-cjk: for Chinese character support in matplotlib
# procps: for process monitoring
# Use tuna mirrors to speed up apt-get
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --fix-missing \
    cron \
    fonts-noto-cjk \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ .

# Copy scripts
COPY docker_scripts/ /app/docker_scripts/
RUN chmod +x /app/docker_scripts/*.sh

# Setup cron job
# Run at 00:00 every day
RUN echo "0 0 * * * /app/docker_scripts/cleanup_charts.sh" > /etc/cron.d/cleanup-cron
RUN chmod 0644 /etc/cron.d/cleanup-cron
RUN crontab /etc/cron.d/cleanup-cron

# Create log file for cron
RUN touch /var/log/cron.log

# Expose port
EXPOSE 8000

# Start command
CMD ["/app/docker_scripts/start.sh"]

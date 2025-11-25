FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y cron tini && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/runner.sh /app/entrypoint.sh

# Set cron job
RUN echo "SHELL=/bin/bash" > /etc/cron.d/jobfetcher \
    && echo "PATH=/usr/local/bin:/usr/bin" >> /etc/cron.d/jobfetcher \
    && echo "TZ=Europe/Helsinki" >> /etc/cron.d/jobfetcher \
    && echo "0 11 * * * cd /app && /app/runner.sh >> /var/log/cron.log 2>&1" >> /etc/cron.d/jobfetcher \
    && chmod 0644 /etc/cron.d/jobfetcher \
    && crontab /etc/cron.d/jobfetcher

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Helsinki
RUN ln -snf /usr/share/zoneinfo/Europe/Helsinki /etc/localtime

EXPOSE 8501

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/entrypoint.sh"]

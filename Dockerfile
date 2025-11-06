FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y cron tini && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN chmod +x /app/runner.sh
RUN echo "0 11 * * * /app/runner.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/jobfetcher
RUN chmod 0644 /etc/cron.d/jobfetcher && crontab /etc/cron.d/jobfetcher

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Helsinki

EXPOSE 8501

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD bash -c "/app/runner.sh && service cron start && streamlit run viewer2.py --server.port=8501 --server.address=0.0.0.0

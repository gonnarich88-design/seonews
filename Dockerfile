FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Bangkok
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

# รันทุกวัน 08:00 Bangkok time (UTC+7)
RUN echo "0 8 * * * cd /app && /usr/local/bin/python3 main.py >> /app/data/cron.log 2>&1" \
    > /etc/cron.d/seonews && \
    chmod 0644 /etc/cron.d/seonews && \
    crontab /etc/cron.d/seonews

VOLUME ["/app/data"]

CMD ["cron", "-f"]

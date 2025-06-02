FROM debian:12.8
RUN apt-get update && apt-get -y install cron curl

WORKDIR /app

COPY update.sh update.sh
COPY update_url update_url
RUN chmod +x update.sh

COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

CMD ["cron", "-f", "/etc/cron.d/cronjob"]
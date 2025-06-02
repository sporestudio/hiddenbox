# This file will be used to deploy the server

include .env

stop:
	@docker-compose down >/dev/null 2>&1

## This section will be used to create a temporary server that will be used by
## certbot, so that if the content of htdocs and letsencrypt works it will generate the certificate.

# First create the apache container
run_temp_apache:
	@docker run -d --rm --name apache_temp \
		-p 8080:80 \
		-v $$PWD/certbot/httpd.conf:/usr/local/apache2/conf/httpd.conf \
		-v $$PWD/certbot/htdocs:/usr/local/apache2/htdocs \
		httpd

# web container used for certbot test
run_certbot:
	@docker run --rm --name certbot \
		-v $$PWD/certbot/htdocs:/data/letsencrypt \
		-v certs:/etc/letsencrypt \
		certbot/certbot \
		certonly --webroot \
		--email ${SERVER_ADMIN} --agree-tos --no-eff-email \
		--webroot-path=/data/letsencrypt \
		-d ${DOMAIN_NAME}

stop_temp_apache:
	@docker stop apache_temp

get_certs: stop run_temp_apache run_certbot stop_temp_apache

deploy:
	@make stop
	@docker-compose up -d

# Deployment of the server with certs
# if we don't want to generate the certificates we only have to do *make deploy*.
all: get_certs deploy
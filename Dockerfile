FROM python:2.7-alpine
LABEL developer="Luciano Alvarez"
RUN apk add --update openssl
WORKDIR /usr/local/bin
COPY dns_proxy_udp.py .
EXPOSE 53
CMD ["python","dns_proxy_udp.py"]

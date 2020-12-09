import socket
import ssl
# import daemon
import logging
import threading
import sys
from time import sleep

RESOLVER_IP_ADDRESS = '1.1.1.1'
IN_PORT = 53
OUT_PORT = 853
PROXY_HOST = 'localhost'


def establish_tls_connection():
    """ Establish a TCP TLS connection with binding pair address/port defined in global vars"""
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        # context.load_verify_locations('./ca-certificates.crt')
        context.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(120)
        wrapped_socket = context.wrap_socket(sock, server_hostname=RESOLVER_IP_ADDRESS)
        wrapped_socket.connect((RESOLVER_IP_ADDRESS, OUT_PORT))
        logging.info(wrapped_socket.getpeercert())
        return wrapped_socket
    except Exception as e:
        logging.error('There was an error establishing tls connection. Error was: {}'.format(e))


def handle_request(query_data, app_address, client_sock_object):
    """ Establish TLS connection, sends a query over it and returns the response the client peer"""
    try:
        tls_sock = establish_tls_connection()
        resolver_response = send_query(tls_sock, query_data)
        client_sock_object.sendto(resolver_response[2:], app_address)
    except Exception as e:
        logging.error('There was an error handling the request. Error was: {}'.format(e))


def send_query(tls_sock, query_data):
    """ Receives a byte object query, adapts the TCP packet according to RFC1035 Section 4.2.2 specification
        https://tools.ietf.org/html/rfc1035#section-4.2.2
        Returns the server response"""
    tcp_query_data = "\x00".encode() + chr(len(query_data)).encode() + query_data
    tls_sock.send(tcp_query_data)
    resolver_response = tls_sock.recv(1024)
    logging.info('DNS resolver response is {}'.format(resolver_response))
    return resolver_response


def serve_connections():
    """ Listen to incoming request over UDP on binding PROXY_HOST:IN_PORT
        Opens a new thread to handle every client request"""
    client_sock_object = init_sock_object()
    while True:
        try:
            query_data, client_address = client_sock_object.recvfrom(1024)
            logging.info('Client {} connected'.format(client_address))
            thread = threading.Thread(target=handle_request, args=(query_data, client_address, client_sock_object,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            logging.error('There was an error handling the request. Error was: {}'.format(e))
            sleep(5)
            continue


def init_sock_object():
    """ Initialize socket connection. Returns socket object"""
    try:
        client_sock_object = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock_object.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_sock_object.bind((PROXY_HOST, IN_PORT))
        logging.info('Socket on {}:{} created succesfully'.format(PROXY_HOST, IN_PORT))
        return client_sock_object
    except socket.error as e:
        logging.error('There was an error Creating the socket. Error was: {}'.format(e))
        return


def init_log_handler():
    """ Initialize logging handler to have proper verbosity and format on stdout"""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


if __name__ == '__main__':
    #with daemon.DaemonContext():
    init_log_handler()
    serve_connections()

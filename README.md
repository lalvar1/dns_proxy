## DNS over TLS
#### Overview
This proxy development can be used to send DNS queries over an encrypted connection, rather than plain text queries, 
using TLS in this case and acting as an intermediate agent between a certain client/application and a DNS resolver, which is CloudFlare
for the current implementation.


### Implementation details and steps
The proxy will create a socket and listen to incoming requests only over port 53.
Once it receives the binary data (TCP/UDP packet), it will open a new thread to process every DNS request.
The processing of the request implies the following tasks:
* Establish a TLS connection with CloudFlare server over port 853, validating the corresponding certs
* Adapt the query to the corresponding TCP format specified in RFC1035
* Send it to DNS resolver and respond back the query result to the client


#### Reference doc (RFCs and libraries)
https://tools.ietf.org/html/rfc1035
https://tools.ietf.org/html/rfc7858
https://docs.python.org/3/library/ssl.html


#### Security aspects
* There are known attacks on TLS, such as person-in-the-middle and protocol downgrade, middleboxes that interfere with the normal resolution, and others.
* All recommendations to address this: https://tools.ietf.org/html/rfc7858#ref-BCP195


#### Source code
* Dockerfile
* dns_proxy_ucp.py
* dns_proxy_tcp.py


#### How to run and test the code
##### Installation
Run as root/sudo the following commands:
* Build the container image by typing <br /> 
docker build -t dns-proxy
* Create a network where the proxy will run <br /> 
docker network create --subnet 172.16.0.0/24 mySubnet
* Run the container using the previously created resources <br /> 
docker run --net mySubnet -it dns-proxy

##### Test
On the same machine, make a dns query pointing the dns proxy host url, specified as **PROXY_HOST** in **dns_proxu_udp.py** file
* dig @172.16.0.2 -p 53 -q google.com <br /> 
* nslookup google.com 172.16.0.2

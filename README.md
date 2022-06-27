# TCP_over_SSL
an encrypted TCP chat server that uses self-signed SSL certification

## General Info
To connect to this server 'remotely', add port forwarding in your router/firewall
that allows traffic forwarding from public IP to localhost (on your Host machine)

## Requirements:
#### Modules:
* socket
* threading
* ssl
#### System packages:
* openSSL

## Usage
connect to this server (as a client) from
a command line on any operating system by
typing the following command:

`$ openssl s_client -quiet -connect PUBLIC_IP:PORT`

`-quiet` is a must to prevent ssl errors.
replace *PUBLIC_IP* and *PORT* with your server's

## Important notes
* openSSL must be installed in order to do a handshake with the server.
* be sure to create .pem file, private.key, ssl certificate to
load certificate chain.

#!/bin/bash -x 

#grep $(hostname) /etc/hosts || sudo bash -c "echo 127.0.0.1 \$(hostname) | tee -a /etc/hosts"
#export PYCURL_SSL_LIBRARY=openssl 
#export CFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"

virtualenv -v -p /usr/bin/python2.7 --setuptools env

#!/bin/bash

fuser -k 80/tcp
fuser -k 8080/tcp
forever stopall
forever start /root/Koder/html/server.js
forever start /root/Koder/ChatApp/index.js
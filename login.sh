#!/bin/bash

DONGLE_IP="192.168.0.1"
PASSWORD="D4275DNZ"

# 1. Fetch LD & RD (no cookie needed, just Referer)
LD=$(curl -s "http://${DONGLE_IP}/goform/goform_get_cmd_process?isTest=false&cmd=LD" \
  -H "Referer: http://${DONGLE_IP}/index.html" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['LD'])")
echo "LD: $LD"
RD=$(curl -s "http://${DONGLE_IP}/goform/goform_get_cmd_process?isTest=false&cmd=RD" \
  -H "Referer: http://${DONGLE_IP}/index.html" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['RD'])")
echo "RD: $RD"

# 2. Compute SHA256(SHA256(password) + RD) — uppercase
INNER=$(echo -n "$PASSWORD" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')
LOGIN_PASS=$(echo -n "${INNER}${LD}" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')
echo "LOGIN_PASS: $LOGIN_PASS"
  
# 3. Login and capture stok cookie
RESPONSE=$(curl -s -c /tmp/zte_cookies.txt -X POST \
  "http://${DONGLE_IP}/goform/goform_set_cmd_process" \
  -H "Accept: application/json, text/javascript, */*; q=0.01" \
  -H "Accept-Encoding: gzip, deflate" \
  -H "Accept-Language: en-GB,en;q=0.7" \
  -H "Connection: keep-alive" \
  -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
  -H "Host: ${DONGLE_IP}" \
  -H "Origin: http://${DONGLE_IP}" \
  -H "Referer: http://${DONGLE_IP}/index.html" \
  -H "Sec-GPC: 1" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d "isTest=false&goformId=LOGIN&password=${LOGIN_PASS}")
  echo "Login response: $RESPONSE"
  STOK=$(grep stok /tmp/zte_cookies.txt | awk '{print $NF}')
  echo "STOK: $STOK"
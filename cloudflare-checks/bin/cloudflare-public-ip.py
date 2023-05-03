#!/usr/bin/env python

from os import environ
import sys
import requests

CLOUDFLARE_SITE = environ["CLOUDFLARE_SITE"]
CLOUDFLARE_TOKEN = environ["CLOUDFLARE_TOKEN"]

MONITOR_RECORDS = sys.argv

try:
    cf_req = requests.get(
        f'https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_SITE}/dns_records',
        headers = {
            'Authorization': f'Bearer {CLOUDFLARE_TOKEN}',
            'Content-Type': 'application/json',
        }
    )
    cf_req.raise_for_status()

    ip_req = requests.get('https://api.ipify.org?format=json')
    ip_req.raise_for_status()
except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as err:
    raise SystemExit(err)

cloudflare = cf_req.json()
ip = ip_req.json()['ip']

for dns_record in cloudflare['result']:
    if dns_record['name'] not in MONITOR_RECORDS or dns_record['type'] not in ('A', 'AAAA'):
        continue
    if dns_record['content'] == ip:
        print(f"OK: Record for {dns_record['name']}={dns_record['content']} matches public IP")
    else:
        print(f"WARNING: Record for {dns_record['name']}={dns_record['content']} doesn't match public IP {ip}!")
        sys.exit(1)

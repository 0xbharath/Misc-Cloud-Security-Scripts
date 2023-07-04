from ipaddress import ip_network, ip_address
import json
import requests
import sys

def find_aws_region():
 ip_json = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
 #ip_json = json.load(open('ip-ranges.json'))
 ip_json = ip_json.json()
 prefixes = ip_json['prefixes']
 my_ip = ip_address(sys.argv[1])
 region = 'Unknown'
 for prefix in prefixes:
   if my_ip in ip_network(prefix['ip_prefix']):
     region = prefix['region']
     print(region)
     break
 return region

if __name__ == "__main__":
   find_aws_region()

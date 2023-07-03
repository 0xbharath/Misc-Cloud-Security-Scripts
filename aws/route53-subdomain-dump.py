#!/usr/bin/env python3

import boto3, jmespath, click, logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

@click.command()
@click.argument('aws_profiles', nargs=-1,required=True, type=str)
def main(aws_profiles):
    """This script dumps all the domain names (hostnames) for all hosted zones on a Route53 instance \n

       Prerequisite for this script - An AWS Named profile with ReadOnly permission to Route53 instance \n
       
       Usage - python3 route53-subdomain-dump.py aws_named_profile1 aws_named_profile2
    """

    subdomains = [] # Empty list for appending subdomains later
    for profile in aws_profiles:
        try:
            logging.info("[+] Enumerating subdomains for profiles - {}".format(profile))
            session = boto3.Session(profile_name=profile)
        except Exception as e:
            print(e)
            logging.error("[!] Error in accessing AWS profile - {}".format(profile))
            continue
        client = session.client('route53')
        hosted_zones = get_hosted_zone_ids(client, profile)
        resource_records = get_resource_records(hosted_zones, client, profile)
        subdomains = get_subdomains(resource_records, subdomains, profile)
    subdomains = set(subdomains) # remove duplicate subdomain

    for subdomain in subdomains:
        print(subdomain)

# To get the list of all hosted zones on Route53 instance
def get_hosted_zone_ids(client, profile):
    logging.info("[+] Getting all the hosted zones on Route53 instance for {}".format(profile))
    hosted_zones = []
    response = client.list_hosted_zones(
        MaxItems="300",
    )
    if ('HostedZones' in response.keys()
        and len(response['HostedZones'])) > 0:
        for i in response['HostedZones']:
            for key in i.keys():
                if key=="Id":
                    hosted_zones.append(i[key].split('/')[2])
    else:
        logging.error("[+] Error in accessing hosted zones on Route53 instance for {}".format(profile))

    return hosted_zones

# To get the list of all resouce record sets for the hosted zones on Route53 instance
def get_resource_records(hosted_zones,client,profile):
    resource_record_sets = []
    #dns_record_types = ['SOA','A','TXT','NS','CNAME','MX','NAPTR','PTR','SRV','SPF','AAAA','CAA','DS']
    paginator = client.get_paginator('list_resource_record_sets')
    for hosted_zone in hosted_zones:
        logging.error("[+] Getting all the DNS resource records for {} - {}".format(hosted_zone, profile))
        paginated_resource_record_sets = paginator.paginate(HostedZoneId=hosted_zone)
        for record_set in paginated_resource_record_sets:
            resource_record_sets.append(record_set)
    
    return resource_record_sets

# To extract subdomains (and filter out subdomains that are not hostnames i.e. with '_', '/' etc
def get_subdomains(resource_records, subdomains, profile):
    logging.info("[+] Parsing the subdomains and extracting subdomains - {}".format(profile))
    for record in resource_records:
        parsed_records = jmespath.search("ResourceRecordSets[].Name",record)
        for parsed_record in parsed_records:
            if '_' not in parsed_record and '\\' not in parsed_record:
                subdomains.append(parsed_record)
    return subdomains

if __name__ == "__main__":
    main()
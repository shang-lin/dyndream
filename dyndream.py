#!/usr/bin/env python

"""
dyndream.py is a program that uses Dreamhost's API to configure dynamic DNS.

"""
import requests
import uuid
import os
import os.path
import sys
import logging
import time

DEFAULT_CONFIG_FILE = ".dyndream"
required_config_fields = ['API_KEY', 'DREAMHOST_URL', 'IP_URL', 'DYNAMIC_URL']
optional_config_fields = ['LOGFILE']
config = {}


def read_config(config_file):
    """ Reads configuration file. """
    print("Reading configuration from {}".format(config_file))
    with open(config_file, 'r') as fh:
        for line in fh.readlines():
            fields = line.strip().split('=',1)
            if fields[0] in required_config_fields or fields[0] in optional_config_fields:
                config[fields[0]] = fields[1]

    for f in required_config_fields:
        if f not in config:
            raise LookupError("No value for {}".format(f))


def get_ip():
    """
    Gets this computer's IP address from a web service.
    """
    response = requests.get(config['IP_URL'])
    ip = response.json()['ip']
    return ip


def send_dreamhost_command(cmd, **kwargs):
    """
    Send a request to the Dreamhost API and return the response in JSON.
    """
    params = "?key={}&cmd={}&unique_id={}&format=json".format(config['API_KEY'], cmd, uuid.uuid1())
    for key, value in kwargs.items():
        params += "&{}={}".format(key, value)
    response = requests.get(config['DREAMHOST_URL'] + '/' + params)
    return response.json()


def get_dns_ip():
    """
    Retrieves the current IP of DYNAMIC_URL from DNS.
    """
    dns = send_dreamhost_command('dns-list_records')
    ip = ''
    for dns_record in dns['data']:
        if dns_record['record'] == config['DYNAMIC_URL'] and dns_record['type'] == 'A':
            ip = dns_record['value']
            logging.info('Found record with IP ' + ip)
    return ip


def update_ip(old_ip, new_ip):
    """
    Sets the A record of DYNAMIC_URL to the current IP.
    """
    resp = send_dreamhost_command('dns-remove_record', record=config['DYNAMIC_URL'], type='A', value=old_ip)
    if resp['result'] == 'error':
        logging.error('Failed to remove old record. Error: ' + resp['data'])
    resp = send_dreamhost_command('dns-add_record', record=config['DYNAMIC_URL'], type='A', value=new_ip)
    if resp['result'] == 'error':
        logging.error('Failed to add record for ' + config['DYNAMIC_URL'] + ' with IP ' + new_ip)
        print('Error:' + resp['data'])
    else:
        logging.info('Changed IP for ' + config['DYNAMIC_URL'] + ' from ' + old_ip + ' to ' + new_ip)


def main():

    if len(sys.argv) >= 2:
        config_file = sys.argv[1]
    else:
        config_file = os.path.join(os.environ['HOME'], DEFAULT_CONFIG_FILE)
        if not os.path.isfile(config_file):
            config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), DEFAULT_CONFIG_FILE)
            if not os.path.isfile(config_file):
                print("Configuration file {} not found in $HOME or in {}'s directory."
                      .format(DEFAULT_CONFIG_FILE, sys.argv[0]))
                sys.exit(2)
    read_config(config_file)

    if 'LOGFILE' in config:
        logfile = config['LOGFILE']
        if not(os.access(logfile, os.W_OK)):
            logfile = ''
            print("Cannot open requested log file {}, logging to stdout"
                  .format(logfile))
    else:
        logfile = ''

    logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO, format='%(message)s')
    logging.info('** Starting {} on {} **'.format(os.path.basename(sys.argv[0]), time.asctime()))
    logging.info('Using config file {}'.format(config_file))
    ip = get_ip()
    old_ip = get_dns_ip()
    if ip == old_ip:
        logging.info("IP address has not changed.")
    else:
        update_ip(old_ip, ip)
    logging.info('** Ending {} on {} **'.format(os.path.basename(sys.argv[0]), time.asctime()))

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Check EC2 instances status.
If instances are stopped, this script wake them up.
"""
from config import *
import os
import boto
import boto.ec2
import sys
import traceback
import time
from optparse import OptionParser

VERSION = '1.0'

class Wakeup:
    def __init__(self):
        self.target_list = {}
        self.instances = []
        self.target_instances = []
        self.instance_list = []


    def main(self, account='default', instance_name=[], region=None):
        if not account in AWS_DATA:
            print 'Account not found!'
            return

        if not instance_name:
            print 'Instances are not defined.\nExit.'
            return
        else:
            self.target_instances = instance_name

        aws_data = AWS_DATA[account]
        self._connect_ec2(aws_data, region)


    def _connect_ec2(self, aws_data, region):
        """
        make connection to EC2.
        """
        if region:
            region_name = REGION[region]
        else:
            region_name = REGION[aws_data['region']]

        print 'Connecting to EC2 (%s)...' % region_name
        try:
            if not aws_data['access_key']:
                self.conn = boto.ec2.connect_to_region(region_name=region_name)
            else:
                self.conn = boto.ec2.connect_to_region( region_name=region_name,
                        aws_access_key_id=aws_data['access_key'],
                        aws_secret_access_key=aws_data['secret_key']
                )

            print '...Done.'
        except:
            print 'EC2 Connection Error!!\n===\nTRACEBACK: %s' % traceback.format_exc()
            return

        self._confirm_instance(1)


    def _confirm_instance(self, start_flg=False):
        """
        Search instance, and start
        """
        reservations = self.conn.get_all_instances()
        instances = [i for r in reservations for i in r.instances]

        target_list = 0
        dns_list = []

        if len(instances) < 1:
            print 'Instance not found.'
            return

        for i, ins in enumerate(instances):
            tmp = {}
            name = ins.tags.get('Name', '(No Tag)')
            if not name in self.target_instances:
                continue

            print '"%s" Status: %s' % (name, ins.update())
            if ins.update() != 'running':
                target_list = 1
                if start_flg:
                    print 'Start "%s"' % name
                    ins.start()

            elif ins.update() == 'running':
                tmp = {'name':name, 'dns':ins.public_dns_name, 'vol-id':ins.block_device_mapping.current_value.volume_id}
                dns_list.append(tmp)

        if target_list or not dns_list:
            print 'Waiting 10sec...'
            time.sleep(10)
            self._confirm_instance()
        else:
            print 'Launch OK.'
            self._confirm_ping(dns_list, True)
            self.instance_list = dns_list


    def _confirm_ping(self, server, display=False):
        check = 1
        dns_list = []

        if not server:
            print 'Server not found'
            return

        if display:
            print 'Checking ping...'

        for s in server:
            cmd = r'ping -c 1 %s >/dev/null' % s['dns']
            ping = os.system(cmd)
            if ping is not 0:
                check = 0

        if not check:
            print 'Waiting 10sec...'
            time.sleep(10)
            self._confirm_ping(server)
        else:
            print 'Ping OK. \nYou can access these servers.'
            print '-' * 60
            for s in server:
                print '%(name)s: %(dns)s' % s
                print '-' * 60



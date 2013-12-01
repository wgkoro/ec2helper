#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Create/Delete snapshot

This script is an arrange of http://heartbeats.jp/hbblog/2011/04/botoebs.html
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

class SnapShot:
    def __init__(self):
        self.conn = None
        self.target_vol = ''
        self.account = 'default'
        self.backup_count = 5
        self.region = ''


    def _create_connection(self):
        if self.conn:
            return 1

        aws = AWS_DATA[self.account]
        if self.region:
            region_id = self.region
        else:
            region_id = aws['region']

        region_name = REGION[region_id]
        print 'Connecting to EC2 (%s)...' % (aws['region'])

        try:
            if not aws['access_key']:
                self.conn = boto.ec2.connect_to_region(region_name=region_name)
            else:
                self.conn = boto.ec2.connect_to_region( region_name=region_name,
                        aws_access_key_id=aws['access_key'],
                        aws_secret_access_key=aws['secret_key']
                )

            print '...Done.'
            return 1
        except:
            print 'EC2 Connection Error!!\n===\nTRACEBACK: %s' % traceback.format_exc()
            return 0


    def create_snapshot(self, description=''):
        if not description:
            print 'Description is not defined!\nexit...'
            return

        if not self._create_connection():
            print 'exit...'
            return

        if not self.conn:
            print 'No Connection...\nexit..'
            return

        print 'Creating Snapshot... (%s, description:%s)' % (self.target_vol, description)
        try:
            self.conn.create_snapshot(volume_id=self.target_vol, description=description)
            print '...Done!'
        except:
            print 'Error!\n==\nTRACEBACK: %s' % traceback.format_exc()
            print '\nexit...'
            return

        snapshot = {}
        for x in self.conn.get_all_snapshots():
            if((x.volume_id == self.target_vol) and (x.description == description)):
                tmp = {x.id:x.start_time}
                snapshot.update(tmp)

        snapshot = sorted(snapshot.items(), key=lambda (k, v): (v, k), reverse=True)
        for i in range(self.backup_count, len(snapshot)):
            self.conn.delete_snapshot(snapshot[i][0])


    def delete_latest_snapshot(self, description=''):
        delimit = '-' * 60

        if not description:
            print 'Description is not defined!\nexit...'
            return

        if not self._create_connection():
            print 'exit...'
            return

        snapshot = {}
        for x in self.conn.get_all_snapshots():
            if x.description == description:
                tmp = {x.id:x.start_time}
                snapshot.update(tmp)

        snapshot = sorted(snapshot.items(), key=lambda (k, v): (v, k), reverse=True)
        count = len(snapshot)
        if count < 1:
            print 'Snapshot(%s) not found.' % description
            return

        target = snapshot[0]
        print '\nList of snapshots'
        print delimit
        for i in range(len(snapshot)):
            print 'Snapshot ID[ %s ] Start-Time[ %s ]' % (snapshot[i][0], snapshot[i][1])
            print delimit

        message = '\nSnapshot ID[ %s ] Start-Time[ %s ] will be deleted. OK? [y/n]: ' % (target[0], target[1])
        answer = ''
        while not answer:
            answer = raw_input(message)
            if answer != 'n' and answer != 'y':
                answer = ''

        if answer == 'n':
            print 'Canceled!\nexit...'
            return

        print 'Deleting "%s"...' % target[0]
        try:
            self.conn.delete_snapshot(target[0])
            print '...Done!'
        except:
            error = traceback.format_exc()
            if error.find('is currently in use') != -1:
                print 'Snapshot currently in use. Deletion aborted.'





if __name__ == '__main__':
    s = SnapShot()

    usage = u'%prog [description] [Options]\nSee -h or --help'
    parser = OptionParser(usage=usage, version=VERSION)

    parser.add_option(
        '-a', '--account',
        action = 'store',
        type = 'str',
        dest = 'account_key',
        help = 'AWS account key'
    )
    parser.add_option(
        '-r', '--region',
        action = 'store',
        type = 'str',
        dest = 'region_id',
        help = 'Region ID'
    )
    parser.add_option(
        '-v', '--vol',
        action = 'store',
        type = 'str',
        dest = 'volume_id',
        help = 'EBS vol-id'
    )
    parser.add_option(
        '-d', '--delete',
        action = 'store_true',
        dest = 'delete',
        help = 'Delete latest snapshot'
    )
    parser.set_defaults(
        account_key = 'default',
        volume_id = '',
        region_id = '',
        delete = False
    )

    options, args = parser.parse_args()
    acc = options.account_key
    delete_flg = options.delete
    volume = options.volume_id
    region = options.region_id

    if not acc in AWS_DATA.keys():
        parser.error('Invalid account_key.')

    if region:
        if not region in REGION.keys():
            parser.error('Invalid region.')

        s.region = region

    if not delete_flg and not volume:
        parser.error('Volume-id not defined.')

    count = len(args)
    if count != 1:
        parser.error('Invalid argument.')

    desc = args[0]
    s.account = acc
    s.target_vol = volume

    if delete_flg:
        s.delete_latest_snapshot(desc)
    else:
        s.create_snapshot(desc)


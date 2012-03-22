#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Main class.
Wake instances up, deploy(Capistrano), create or delete snapshot.
"""
import os
import traceback
from wakeup import Wakeup
from snapshot import SnapShot
from optparse import OptionParser

VERSION = 1.0

class Config:
    def __init__(self):
        self.base_command = 'cd %(cap_path)s;cap %(deploy_to)s %(cap_command)s -S host=%(target)s'
        self.cap_allow_command = [
            'deploy',
            'deploy:rollback',
            'deploy:cleanup'
        ]
        self.create_snapshot = False
        self.snap_description = ''
        self.create_snap_only_production = True


class Deploy:
    def __init__(self, config):
        self.w = Wakeup()
        self.cap_command = {}
        self.instance_names = []
        self.conf = config
        self.region = ''


    def start(self):
        usage = u'%prog [deploy_to(p/d)] [deploy_command] [Options]'
        parser = OptionParser(usage=usage, version=VERSION)

        parser.add_option(
            '-r', '--region',
            action = 'store',
            type = 'str',
            dest = 'region_id',
            help = 'Region ID'
        )
        parser.set_defaults(
            region_id = ''
        )

        options, args = parser.parse_args()
        self.region = options.region_id

        count = len(args)
        if count != 2:
            parser.error('Invalid command.')
        else:
            to = args[0]
            command = args[1]
            if not to in self.conf.cap_deploy_to.keys():
                parser.error('Specify "deploy_to"')

            if not command in self.conf.cap_allow_command:
                parser.error('Specify "deploy_command"')

        self.cap_command['deploy_to'] = self.conf.cap_deploy_to[to]
        self.cap_command['cap_command'] = command
        self.instance_names = self.conf.instances[to]
        self._main()


    def _main(self):
        self.w.main(self.conf.aws_account, self.instance_names, self.region)
        if not self.w.instance_list:
            print 'exit.'
            return

        message = '\nStart %s? ### TARGET:"%s" ### [y/n]: ' % (self.cap_command['cap_command'], self.cap_command['deploy_to'])
        com = ''
        while not com:
            com = raw_input(message)
            if com != 'n' and com != 'y':
                com = ''

        if com == 'n':
            print 'Canceled!\nexit...'
            return

        self.cap_command['target'] = ','.join([i['dns'] for i in self.w.instance_list])
        self.cap_command['cap_path'] = self.conf.cap_path
        command = self.conf.base_command % self.cap_command
        os.system(command)

        self._snapshot()


    def _snapshot(self):
        if not self.conf.create_snapshot or self.cap_command['cap_command'] == 'deploy:cleanup':
            return

        if self.conf.create_snap_only_production and self.cap_command['deploy_to'] == self.conf.cap_deploy_to['d']:
            return

        if not self.conf.snap_description:
            print 'Snapshot description not defined.\nexit...'
            return

        if not self.w.instance_list:
            print 'Instance not found!\nexit...'
            return

        target = self.w.instance_list[0]
        if not target:
            print 'Target not found!\nexit...'
            return

        s = SnapShot()
        s.conn = self.w.conn
        s.target_vol = target['vol-id']
        create = True
        
        if self.cap_command['cap_command'] == 'deploy':
            message_snap = '\nCreate snapshot? (%s) [y/n]: ' % target['name']
        else:
            message_snap = '\nDelete last snapshot? [y/n]: '
            create = False

        com = ''
        while not com:
            com = raw_input(message_snap)
            if com != 'n' and com != 'y':
                com = ''

        if com == 'n':
            print 'Canceled!\nexit...'
            return

        if create:
            s.create_snapshot(self.conf.snap_description)
        else:
            s.delete_latest_snapshot(self.conf.snap_description)


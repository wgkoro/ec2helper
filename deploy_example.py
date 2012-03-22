#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ec2helper.wakeup import Wakeup
from ec2helper.deploy import Deploy, Config

conf = Config()

# Edit ================================================
conf.aws_account = 'default'
conf.instances = {
    'p' : ['production_server1', 'production_server2'],
    'd' : ['dev_server'],
}

conf.cap_path = '/path/to/cap/directory'
conf.cap_deploy_to = {
    'p' : 'production',
    'd' : 'dev',
}

#conf.create_snapshot = True
#conf.snap_description = 'snapshot test'
#conf.create_snap_only_production = False
# =====================================================


if __name__ == '__main__':
    d = Deploy(conf)
    d.start()

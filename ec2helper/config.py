#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
EC2tools config
"""

REGION = {
    't'     : 'ap-northeast-1', # TOKYO
    's'     : 'ap-southeast-1', # SINGAPORE
    'v'     : 'us-east-1', # US East(Virginia)
    'o'     : 'us-west-2', # US West(Oregon)
    'n'     : 'us-west-1', # US West(N. California)
    'e'     : 'eu-west-1', # EU West(Ireland)
    'sa'    : 'sa-east-1', # S. America(Sao Paulo)
}

AWS_DATA = {
    'default'   : {
        'access_key'    : 'ACCESSKEYACCESSKEY',
        'secret_key'    : 'SECRETKEYSECRETKEYSECRETKEYSECRETKEY',
        'region'    : 't',
    },
    'account_2'   : {
        'access_key'    : 'ACCESSKEYACCESSKEY',
        'secret_key'    : 'SECRETKEYSECRETKEYSECRETKEYSECRETKEY',
        'region'    : 's',
    },
}

import pulumi
import yaml
from asg import Asg,AsgArgs

config = pulumi.Config()

BASE_TAGS={
    'Environment': 'demo',
    'SomeValue': config.get('some_value', 'true'),
    'SomeNumericValue': config.require_int('some_numeric_value'),
    'SomeSecretValue': config.require('some_secret_value')
}

with open('legacy-us.yaml') as luf:
    vpc_legacy_us = yaml.load(luf, Loader=yaml.Loader)

with open('test.yaml') as tf:
    vpc_test = yaml.load(tf, Loader=yaml.Loader)

# vpc = vpc_legacy_us
vpc = vpc_test

asg = Asg(
    'demo',
    AsgArgs(
        ami_id=vpc.get('InstanceAmi'),
        base_tags=BASE_TAGS,
        instance_size=config.require('instance_size'),
        private_subnet_ids=[
            vpc['PrivateSubnet1'],
            vpc['PrivateSubnet2']
        ],
        vpc_id=vpc['VpcId']
    )
)

pulumi.export('asg-secgrp-id', asg.asg_security_group.id)
pulumi.export('autoscaling-group-id', asg.as_group.id)

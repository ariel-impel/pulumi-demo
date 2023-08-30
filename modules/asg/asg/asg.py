import pulumi
import pulumi_aws as aws
from typing import Mapping, Sequence

class AsgArgs:
    def __init__(self,
                 ami_id: pulumi.Input[str],
                 base_tags: Mapping[str,str],
                 instance_size: pulumi.Input[str],
                 private_subnet_ids: Sequence[str],
                 vpc_id: pulumi.Input[str]):

        self.ami_id = ami_id
        self.base_tags = base_tags
        self.instance_size = instance_size
        self.private_subnet_ids = private_subnet_ids
        self.vpc_id = vpc_id


class Asg(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 args: AsgArgs,
                 opts: pulumi.ResourceOptions = None):

        super().__init__('Asg', name, None, opts)

        self.name = name
        self.ami_id = args.ami_id
        self.base_tags = args.base_tags
        self.instance_size = args.instance_size
        self.private_subnet_ids = args.private_subnet_ids
        self.vpc_id = args.vpc_id

        self.asg_security_group = aws.ec2.SecurityGroup(
            f"{self.name}-asg-secgrp",
            description="Asg security group",
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol='tcp',
                    from_port=22,
                    to_port=22,
                    cidr_blocks=['0.0.0.0/0']
                )
            ],
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol='-1',
                    from_port=0,
                    to_port=0,
                    cidr_blocks=['0.0.0.0/0']
                )
            ],
            vpc_id=self.vpc_id,
            tags=self.base_tags,
            opts=pulumi.ResourceOptions(
                parent=self
            )
        )

        self.launch_template = aws.ec2.LaunchTemplate(
            f"{self.name}-launch-template",
            image_id=self.ami_id,
            instance_type=self.instance_size,
            block_device_mappings=[
                aws.ec2.LaunchTemplateBlockDeviceMappingArgs(
                    device_name='/dev/xvda',
                    ebs=aws.ec2.LaunchTemplateBlockDeviceMappingEbsArgs(
                        delete_on_termination="True",
                        iops=0,
                        volume_size=20,
                        volume_type="gp2"
                    )
                )
            ],
            vpc_security_group_ids=[
                self.asg_security_group.id
            ],
            opts=pulumi.ResourceOptions(
                parent=self
            )
        )

        self.as_group = aws.autoscaling.Group(
            f"{self.name}-asg",
            desired_capacity=1,
            instance_refresh=aws.autoscaling.GroupInstanceRefreshArgs(
                strategy='Rolling'
            ),
            max_size=2,
            min_size=0,
            launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
                id=self.launch_template.id,
                version="$Latest"
            ),
            name_prefix="pulumi_demo",
            tags=[
                aws.autoscaling.GroupTagArgs(
                    key=new_key,
                    value=self.base_tags[new_key],
                    propagate_at_launch=True
                ) for new_key in self.base_tags.keys()
            ],
            vpc_zone_identifiers=self.private_subnet_ids,
            opts=pulumi.ResourceOptions(
                parent=self.launch_template
            )
        )

        super().register_outputs({})

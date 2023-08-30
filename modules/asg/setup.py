from setuptools import setup, find_packages

setup(
    name='asg',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'pulumi',
        'pulumi_aws'
    ]
)

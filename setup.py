#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

setup(
    name='fapistrano',
    version='0.5.1',
    license='MIT',
    description='Capistrano style deployment with fabric',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    packages=['fapistrano'],
    install_requires=[
        'Fabric',
        'requests',
        'PyYaml',
    ],
    entry_points='''
        [console_scripts]
        fap=fapistrano.cli:fap
    '''
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

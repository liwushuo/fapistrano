#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Fabric',
    'requests',
    'PyYaml',
    'click',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='fapistrano',
    version='0.9.3',
    license='MIT',
    description="A remote server automation and deployment tool.",
    long_description=readme + '\n\n' + history,
    zip_safe=False,
    include_package_data=True,
    install_requires=requirements,
    platforms='any',
    author="Ju Lin",
    author_email='soasme@gmail.com',
    url='https://github.com/liwushuo/fapistrano',
    packages=find_packages(),
    package_dir={'fapistrano': 'fapistrano'},
    entry_points="""
    [console_scripts]
    fap=fapistrano.cli:fap
    """,
    keywords='fapistrano, deploy, deployment, automate, automation, fabric, remote, production, staging, development',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

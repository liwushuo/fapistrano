from setuptools import setup


setup(
    name='fapistrano',
    version='0.1.0',
    license='MIT',
    description='Capistrano style deployment with fabric',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    packages=['fapistrano'],
    install_requires=[
        'Fabric',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

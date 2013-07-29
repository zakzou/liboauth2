#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(
        name = 'liboauth2',
        version = '0.0.3',
        keywords = ('OAuth2 Client', 'OAuth2'),
        description = 'Light Python wrapper for the OAuth 2.0 protocol',
        long_description = 'See http://github.com/zakzou/liboauth2',
        license = 'MIT',

        url = 'http://github.com/zakzou/liboauth2',
        author = 'zakzou',
        author_email = 'zakzou@live.com',

        packages = find_packages(),
        include_package_data = True,
        platforms = 'any',
        install_requires = ['pycurl>=7.19.0'],
        classifiers=[
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            ],
        )

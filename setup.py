# -*- coding: utf8 -*-
# vim:set et ts=8 sw=4:

import setuptools

with open('README.md', encoding='utf-8') as readme:
    long_description = readme.read()
    long_description_content_type = 'text/markdown',


name = 'fetch-ethercodes'
description = ''

setup_params = dict(
    name = name,
    version = '0.2',
    author = 'Hans-Peter Jansen',
    author_email = 'hpj@urpla.net',
    description = description or name,
    long_description = long_description,
    long_description_content_type = long_description_content_type,
    url = 'https://github.com/frispete/' + name,
    license = 'MIT',
    py_modules = ['fetch_ethercodes'],
    python_requires = '>=3',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points = {
        'console_scripts': [
            'fetch-ethercodes = fetch_ethercodes:main',
        ],
    },
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)

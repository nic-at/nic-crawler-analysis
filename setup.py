# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='nic_crawler_analysis',
    version='0.1',
    packages=find_packages(),
    url='',
    license='',
    author='Clemens Moritz',
    author_email='clemens.moritz@nic.at',
    description='Python library that collects code used to analyze crawler data',
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        'nose',
        'future',
        'typing',
        'langdetect',
        'beautifulsoup4',
        'tldextract'
    ],
    scripts=[
        'nic_crawler_analysis/scripts/nca_analyze_html'
    ]
)

# coding: utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import unicode_literals
from setuptools import setup, find_packages
import io
import os

here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.rst'), encoding="utf8").read()

version = '0.5.1'
author = 'Piotr Śniegowski'
description = "Service-Arguments"

setup(
    name='service-arguments',
    version=version,
    description=description,
    long_description=README,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django'
    ],
    keywords='django arguments service docker container environment variables 12factor',
    author=author,
    url='http://github.com/sniegu/service-arguments',
    license='MIT License',
    packages=find_packages(),
    platforms=["any"],
    include_package_data=True,
    test_suite='arguments.test.load_suite',
    zip_safe=False,
    install_requires = [
        'six',
        'path.py',
        'jinja2',
        'tabulate',
    ],
    entry_points={
        'console_scripts': [
            "service-arguments=arguments.process:entry_main",
        ],
    }
)

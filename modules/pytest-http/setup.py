#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego pytest-http.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-http',
    version='0.1.0',
    author='Piotr Śniegowski',
    author_email='piotr.sniegowski@gmail.com',
    maintainer='Piotr Śniegowski',
    maintainer_email='piotr.sniegowski@gmail.com',
    license='MIT',
    url='https://github.com/sniegu/pytest-http',
    description='A simple plugin to use with Pytest',
    long_description=read('README.rst'),
    py_modules=['pytest_http'],
    install_requires=[
        'pytest>=2.9.2,<=7.2.2',
        'beautifulsoup4>=4.5.3',
        'cached-property>=1.3.0',
        'requests>=2.9.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'http = pytest_http',
        ],
    },
)

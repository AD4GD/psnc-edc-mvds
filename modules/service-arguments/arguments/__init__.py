# coding: utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .group import Group
from .context import Context
from .service import Service

VERSION = '0.5.0'
__author__ = 'Piotr Śniegowski'
__version__ = tuple(VERSION.split('.'))

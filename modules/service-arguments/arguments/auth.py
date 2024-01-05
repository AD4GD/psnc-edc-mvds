# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .base import TypeScheme, TypeSchemeMetaclass
from .exceptions import ImproperlyPassedArguments, ImproperlySpecifiedArguments

class UserPassword(TypeScheme):

    def _parse_decoded(self, value, provider):
        user, password = value.split(':')
        return {
            'USER': user,
            'PASSWORD': password,
        }

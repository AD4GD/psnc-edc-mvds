# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option


class Command(BaseCommand):

    help = 'Introspects arguments'

    option_list = BaseCommand.option_list + (
        make_option('--show',
            action='store_const',
            const='show',
            dest='command',
            default=None,
            help='Show all options.'),
        )

    # def add_arguments(self, parser):
    #     parser.add_argument('tenant_name', nargs='?')

    def handle(self, *args, **options):
        from tabulate import tabulate

        command = options['command']
        if command == 'show':
            from django.conf import settings
            parser = settings.PARSER

            table = []
            for group in parser.groups:
                for number, argument in enumerate(group.arguments):
                    table.append(('' if number else group.name, argument.name, argument.default))


            print(tabulate(table))

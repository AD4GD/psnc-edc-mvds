# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
import sys

import argparse
from .context import Context
from .base import PyPath
from tabulate import tabulate


def entry_main():
    main(*sys.argv[1:])

def generate_parser():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument(
        '--directories', '-d',
        dest='directories',
        default=[],
        action='append',
    )

    parser.add_argument(
        '--root',
        dest='root',
        action='store',
        default=None,
    )

    parser.add_argument(
        '--target', '-t',
        dest='target',
        action='store',
        default=None,
    )

    parser.add_argument(
        '--color', '-c',
        dest='highlight',
        action='store_true',
        default=False,
    )

    parser.add_argument(
        'command',
        type=str,
        choices=['process', 'validate', 'help', 'render', 'show', 'templates'],
        # action='store',
        # nargs=1,
    )
    return parser


def main(*argv):

    parser = generate_parser()
    args = parser.parse_args(argv)

    if args.directories:
        directories = args.directories
    else:
        directories = ['/etc/arguments']

    context = Context(directories=directories)
    if args.command == 'process':
        context.process(root=args.root)
    elif args.command == 'render':
        output = context.render(target=args.target, highlight=args.highlight)
        # if args.highlight:
        #     output = context.highlight(target=args.target)
        print(output)
    elif args.command == 'show':
        table = []
        for group in context.groups:
            for number, argument in enumerate(group.arguments):
                table.append(('' if number else group.name, argument.name, context.parser.get_value(argument.name), argument.default))

        print(tabulate(table))
    elif args.command == 'templates':
        table = []
        for service in context._services:
            for target, source in service.templates.items():
                table.append((target, source))

        print(tabulate(table))





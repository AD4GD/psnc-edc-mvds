from pprint import pformat

from django.core.management.base import BaseCommand, CommandError


class BaseIndexCommand(BaseCommand):
    index = None
    actions = ("--create", "--populate", "--single", "--delete", "--rebuild", "--status")

    def add_arguments(self, parser):
        parser.add_argument(
            "--create",
            action="store_const",
            dest="action",
            const="create",
            help="create appropriate index in the elasticsearch",
        )
        parser.add_argument("--populate", action="store_const", dest="action", const="populate", help="populate index")
        parser.add_argument("--single", help="index single record with given identifier")
        parser.add_argument("--delete", action="store_const", dest="action", const="delete", help="delete index")
        parser.add_argument(
            "--rebuild",
            action="store_const",
            dest="action",
            const="rebuild",
            help="delete index, recreate and populate it",
        )
        parser.add_argument("--status", action="store_const", dest="action", const="status", help="print index status")
        parser.add_argument(
            "--refresh", action="store_true", help="force refresh to make all performed operations available for search"
        )
        parser.add_argument("-f", "--force", action="store_true", dest="force", help="force operations without asking")
        parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="fail quietly")
        parser.add_argument(
            "--ignore-existing",
            action="store_true",
            dest="ignore_existing",
            help="for create action, do nothing if index exists",
        )

    def get_indexer(self, options):
        raise NotImplementedError

    def get_action(self, options):
        if options["single"]:
            return "single"

        return options["action"] or ""

    def _index_exists(self, options):
        if not self.index.exists():
            self._error("Index does not exist.", options)
            return False

        return True

    def _error(self, msg, options):
        if options["quiet"]:
            self.stderr.write(self.style.WARNING(msg))
        else:
            raise CommandError(msg)

    def single(self, options):
        if self._index_exists(options):
            self.get_indexer(options).single(options["single"])

    def populate(self, options):
        if self._index_exists(options):
            self.get_indexer(options).populate()
            self.stderr.write(self.style.SUCCESS("Index populated."))

    def create(self, options):
        if self.index.exists():
            if options["force"]:
                self.index.delete()
            elif options["ignore_existing"]:
                self.stderr.write(self.style.WARNING("Index already exists, finishing without any action."))
                return
            else:
                self._error("Index already exists.", options)
                return

        self.index.create()
        self.stderr.write(self.style.SUCCESS("Index created."))

    def delete(self, options):
        if not options["force"]:
            response = input("Are you sure you want to delete the index? [n/Y]: ")
            if response.lower() != "y":
                self.stdout.write("Aborted")
                return False

        self.index.delete(ignore=404)
        self.stderr.write(self.style.SUCCESS("Index deleted."))
        return True

    def rebuild(self, options):
        if not self.delete(options):
            return

        self.create(options)
        self.populate(options)

    def status(self, options):
        if self._index_exists(options):
            self.stdout.write("Number of records: {}".format(self.index.search().count()))

            if options["verbosity"] > 1:
                self.stdout.write("Index info:")
                self.stdout.write(pformat(self.index.get()))

    def handle(self, **options):
        action = self.get_action(options)

        try:
            handler = getattr(self, action)
        except AttributeError as e:
            raise CommandError("Invalid action. Must be one of: {}.".format(", ".join(self.actions))) from e

        try:
            handler(options)
        except CommandError:
            # reraise exception
            raise
        except Exception as e:  # pylint: disable=W0703
            self._error("Indexing failed: " + str(e), options)

        if options["refresh"]:
            self.index.refresh()


class BaseIndexer:
    def __init__(self, logger):
        self.logger = logger
        self._retry = False

    def single(self, identifier, silent_fail=False, reason=None):
        """
        Index single record identified with `identifier`.

        :param identifier: identifier of the record to index
        :param silent_fail: if true, do not raise exceptions
        :param reason: indexing reason
        :type reason: str
        :return: status indicating whether indexing should be retried
        :rtype: bool
        """
        raise NotImplementedError

    def populate(self):
        """
        Scan source data store and populate index.

        :return: status indicating whether indexing should be retried
        :rtype: bool
        """
        raise NotImplementedError

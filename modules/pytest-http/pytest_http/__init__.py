# -*- coding: utf-8 -*-
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego pytest-http.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************

import pytest


pytest.register_assert_rewrite("pytest_http.drivers")
pytest.register_assert_rewrite("pytest_http.wrapped_property")


def pytest_assertrepr_compare(op, left, right):
    # deffer import to allow to register_assert_rewrite before
    from .wrapped_property import WrappedProperty

    # TODO: some operators are still missing here
    # TODO: wording of expected/found does not allign properly with operators
    # like greater then equal, etc.
    if isinstance(left, WrappedProperty):
        if op in ['!=', '==', '<', '<=', '>', '>=']:
            return [
                '%r %s %r' % (left, op, right),
                'expected: %r' % (right, ),
                'found:    %r' % (left.value, ),
            ] + left.response.as_lines()

        return [ '%r %s %r' % (left, op, right) ] + left.response.as_lines()

    if isinstance(right, WrappedProperty):
        if op in ['!=', '==', '<', '<=', '>', '>=']:
            return [
                '%r %s %r' % (left, op, right),
                'expected: %r' % (left, ),
                'found:    %r' % (right.value, ),
            ] + right.response.as_lines()

        if op == 'in':
            return [
                '%r %s %r' % (left, op, right),
                'found: %s' % (repr(right.value)[:1000] )
            ] + right.response.as_lines()

        return [ '%r %s %r' % (left, op, right) ] + right.response.as_lines()



def pytest_addoption(parser):

    parser.addoption("--stack-tests", action="store_true", default=False, dest='stack_tests', help="run tests against a stack instance")
    parser.addoption("--print-requests", action="store_true", default=False, dest='print_requests', help="print requests content during tests")


def pytest_configure(config):
    # deffer import to allow to register_assert_rewrite before
    from .drivers import base

    # register an additional marker
    config.addinivalue_line("markers", "stack_only: mark test to run only in stack tests")
    config.addinivalue_line("markers", "synth_only: mark test to run only in synth tests")
    base.BaseDriver.print_requests = config.getoption('print_requests')

def pytest_runtest_setup(item):
    stack_only_marker = item.get_closest_marker("stack_only")
    if stack_only_marker is not None:
        if not item.config.getvalue('stack_tests'):
            pytest.skip("test is marked as stack only - pass --stack-tests to run")

    synth_only_marker = item.get_closest_marker("synth_only")
    if synth_only_marker is not None:
        if item.config.getvalue('stack_tests'):
            pytest.skip("test is marked as synth only - drop --stack-tests to run")


@pytest.fixture(scope='session')
def stack_tests_flag(request):
    return request.config.getvalue('stack_tests')


@pytest.fixture(scope='function')
def stack_tests_switch(request, stack_tests_flag):

    def switch(true_fixture, false_fixture):
        return request.getfixturevalue(true_fixture if stack_tests_flag else false_fixture)

    return switch

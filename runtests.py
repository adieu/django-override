#!/usr/bin/env python
import sys
from os.path import dirname, abspath, join
from optparse import OptionParser

PACKAGE_ROOT = dirname(abspath(__file__))
sys.path.insert(0, PACKAGE_ROOT)

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test.db',
            }
        },
        INSTALLED_APPS=[
            'override',
            'tests.fake_app1',
            'tests.fake_app2',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
        TEMPLATE_DIRS=(
            join(PACKAGE_ROOT, "tests", "templates"),
            join(PACKAGE_ROOT, "tests", "base_templates"),
        ),
        TEMPLATE_LOADERS=(
            'override.loader.FileSystemLoader',
            'override.loader.AppDirectoriesLoader',
        ),
    )

from django_nose import NoseTestSuiteRunner


def runtests(*test_args, **kwargs):
    if not test_args:
        test_args = ['tests']

    kwargs.setdefault('interactive', False)

    test_runner = NoseTestSuiteRunner(**kwargs)

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=0, type=int)
    parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)

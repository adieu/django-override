from setuptools import setup, find_packages

version = '0.1'

tests_require = [
    'django-nose',
]

setup(name='django-override',
      version=version,
      description="Override existing django templates with ease.",
      author='Adieu',
      author_email='adieu@adieu.me',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      tests_require=tests_require,
      extras_require={'test': tests_require},
      test_suite='runtests.runtests',
      include_package_data=True,
      zip_safe=False,
      )

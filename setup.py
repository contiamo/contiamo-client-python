from distutils.command.build_py import build_py
import os
from setuptools import setup, find_packages
import sys
import warnings

from pip._internal.download import PipSession
from pip._internal.req import parse_requirements


path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

requirements = parse_requirements('requirements.txt', session=PipSession())
test_requirements = parse_requirements('requirements-dev.txt', session=PipSession())

requirements = [str(x.req) for x in requirements]
test_requirements = [str(x.req) for x in test_requirements]

if sys.version_info < (3,):
    warnings.warn(
        'Python 2 is not officially supported by Contiamo. '
        'If you have any questions, please file an issue on Github or '
        'contact us at support@contiamo.com.',
        DeprecationWarning)

# Don't import contiamo module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contiamo'))
from version import VERSION

setup(
    name='contiamo',
    cmdclass={'build_py': build_py},
    version=VERSION,
    description='Contiamo Python client',
    author='Contiamo',
    author_email='support@contiamo.com',
    url='https://github.com/contiamo/contiamo-client-python',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    use_2to3=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])

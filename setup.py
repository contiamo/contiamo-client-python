from distutils.command.build_py import build_py
import os
import sys
import warnings

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

install_requires = [
    'isoweek >= 1.3',
    'numpy >= 1.14',
    'pandas >= 0.22',
]

if sys.version_info < (3,):
    warnings.warn(
        'Python 2 is not officially supported by Contiamo. '
        'If you have any questions, please file an issue on Github or '
        'contact us at support@contiamo.com.',
        DeprecationWarning)
    install_requires.append('requests >= 0.8.8, < 0.10.1')
    install_requires.append('ssl')
else:
    install_requires.append('requests >= 0.8.8')

# Don't import contiamo module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contiamo'))
from version import VERSION

setup(
    name='contiamo',
    cmdclass={'build_py': build_py},
    version=VERSION,
    description='Contiamo Python client',
    # long_description=long_description,
    author='Contiamo',
    author_email='support@contiamo.com',
    url='https://github.com/contiamo/contiamo-client-python',
    packages=['contiamo', 'contiamo.tests'],
    # package_data={'contiamo': ['data/ca-certificates.crt']},
    install_requires=install_requires,
    # test_suite='contiamo.test.all',
    tests_require=['pytest >= 3.4'],
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

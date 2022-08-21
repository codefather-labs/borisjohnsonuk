#!/usr/bin/env python3
import os
import sys

from setuptools import find_packages, setup

import __doc__


def get_version():
    return '.'.join(map(str, __doc__.__version__))


try:
    version = get_version()
except ImportError:
    sys.path.append(os.path.join(os.path.dirname('borisjohnsonuk')))
    version = get_version()

install_requires = [x for x in str(open('requirements.txt', 'r').read()).split("\n")]

setup(
    name='pdf-to-markdown-converter (Boris Johnson UK)',
    version=version,
    url='https://github.com/codefather-labs/borisjohnsonuk',
    author=__doc__.__author__,
    description=__doc__.description,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    license='GNU General Public License v3.0 License',
)

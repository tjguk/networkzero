#
# Initially copied from:
# https://raw.githubusercontent.com/pypa/sampleproject/master/setup.py
#

from setuptools import setup, find_packages
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='networkzero',

    version='0.1',

    description='Making networking simple for teachers',
    long_description=long_description,

    url='https://github.com/tjguk/networkzero',

    author='Tim Golden',
    author_email='mail@timgolden.me.uk',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='networking education',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['pyzmq', 'netifaces'],
)

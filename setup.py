#!/usr/bin/env python2

from setuptools import setup, find_packages


install_requires = [
		'argparse',
		'matplotlib',
		'numpy',
		'wxPython',
		]

tests_require = [
		'nose',
		'unittest2',
		]


setup(
	name='Boltzmannizer',
	version='0.1',
	author='Dmitri Iouchtchenko',
	author_email='diouchtc@uwaterloo.ca',
	description='Visualization tool for discrete Boltzmann distributions.',
	license='MIT',
	url='https://github.com/0/Boltzmannizer',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
	],
	install_requires=install_requires,
	tests_require=tests_require,
	packages=find_packages(),
	scripts=[
		'bin/boltzmannizer',
	],
	test_suite='nose.collector',
)

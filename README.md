# The Boltzmannizer

Visualization tool for discrete Boltzmann distributions.

## Installation

The easy way: `pip install Boltzmannizer`

The less-easy way: `python setup.py install`

Requires:

* [`argparse`](https://pypi.python.org/pypi/argparse/)
* [`matplotlib`](http://matplotlib.org/)
* [`numpy`](http://www.numpy.org/)
* [`wxPython`](http://wxpython.org/)

Note that `wxPython` can't be installed through `pip`, so you will need to install it manually first.

This package should be compatible with both Python 2.6 and 2.7, and has been tested on Linux and Mac OS X.

It is highly recommended that this package is installed and run inside a [virtualenv](http://www.virtualenv.org/). The `wxPython` dependency makes this non-trivial, but it is still possible. The use of [wheels](http://wheel.readthedocs.org) is also encouraged, as they make the virtualenv experience _much_ better.

## Running

Run it using the provided `bin/boltzmannizer` script.

## Testing

`python setup.py test`

Requires:

* [`nose`](https://nose.readthedocs.org/en/latest/)
* [`unittest2`](https://pypi.python.org/pypi/unittest2)

For a more manual approach, install the test dependencies and run all the tests with `nosetests` from the root directory.

`unittest2` is used to get new `unittest` features on old versions of Python.

## License

This project is released under the MIT license. See the `LICENSE` file for details.

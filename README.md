# The Boltzmannizer

Visualization tool for discrete Boltzmann distributions.

## Installation

`python setup.py install`

Requires:

* [`argparse`](https://pypi.python.org/pypi/argparse/)
* [`matplotlib`](http://matplotlib.org/)
* [`wxPython`](http://wxpython.org/)

Note that `wxPython` can't be installed through `pip`, so you will need to install it manually first.

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

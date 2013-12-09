from nose.tools import eq_
from unittest2 import main, TestCase

from boltzmannizer.tools.misc import memoized


class MemoizedTest(TestCase):
	def testMultiple(self):
		"""
		Check that the decorator works and that multiple functions with the
		decorator don't clash.
		"""

		num_fs = 3
		num_args = 10
		num_calls = 5

		records = [[0] * num_args for _ in xrange(num_fs)]
		results = [[] for _ in xrange(num_fs)]

		@memoized
		def record_call0(i):
			records[0][i] += 1

			return 2 * i

		@memoized
		def record_call1(i):
			records[1][i] += 1

			return 3 * i

		@memoized
		def record_call2(i):
			records[2][i] += 1

			return 4 * i

		for i in xrange(num_args):
			for _ in xrange(num_calls):
				results[0].append(record_call0(i))
				results[1].append(record_call1(i))
				results[2].append(record_call2(i))

		records_expected = [[1] * num_args for _ in xrange(num_fs)]
		results_expected = []

		results_expected.append([2 * i for i in xrange(num_args) for _ in xrange(num_calls)])
		results_expected.append([3 * i for i in xrange(num_args) for _ in xrange(num_calls)])
		results_expected.append([4 * i for i in xrange(num_args) for _ in xrange(num_calls)])

		eq_(records, records_expected)
		eq_(results, results_expected)


if __name__ == '__main__':
	main()

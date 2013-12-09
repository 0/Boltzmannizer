from nose.tools import eq_
from unittest2 import main, TestCase

from boltzmannizer.tools.misc import memoized, Reserver


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


class ReserverTest(TestCase):
	def testEmpty(self):
		"""
		A useless Reserver with nothing to reserve.
		"""

		OVERFLOW = 'o'

		r = Reserver([], OVERFLOW)

		for _ in xrange(10):
			eq_(r.allocate(), OVERFLOW)

		for _ in xrange(10):
			r.free(OVERFLOW)

		with self.assertRaises(ValueError):
			r.free(OVERFLOW + OVERFLOW)

	def testSeveral(self):
		"""
		A less useless Reserver.
		"""

		OVERFLOW = 'o'

		r = Reserver(['z', 'y', 'x'], OVERFLOW)

		results = []

		# Make some allocations and frees in an arbitrary order and check that
		# priority is given to the earlier items.
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())
		r.free('z')
		r.free('y')
		r.free('x')
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())
		r.free('x')
		r.free('z')
		r.free('y')
		results.append(r.allocate())
		results.append(r.allocate())
		r.free('y')
		results.append(r.allocate())
		r.free('z')
		r.free('x')
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())
		r.free('x')
		r.free('z')
		results.append(r.allocate())
		results.append(r.allocate())
		results.append(r.allocate())

		expected = [
				'z', 'y', 'x', 'o',
				'z', 'y', 'x', 'o', 'o',
				'z', 'y',
				'y',
				'z', 'x', 'o',
				'z', 'x', 'o',
				]

		eq_(results, expected)


if __name__ == '__main__':
	main()

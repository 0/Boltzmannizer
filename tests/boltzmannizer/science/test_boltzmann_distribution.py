from nose.tools import assert_almost_equal, eq_
from os.path import join
from unittest2 import main, TestCase

from numpy.testing import assert_array_almost_equal, assert_array_equal

from boltzmannizer.science.boltzmann_distribution import BoltzmannDistribution, NonIncreasingEnergies


TEST_DATA = join('tests', 'data')


class BoltzmannDistributionTest(TestCase):
	def testEmpty(self):
		"""
		A distribution with nothing in it!
		"""

		bd = BoltzmannDistribution(1, [], [])

		eq_(list(bd.levels), [])
		eq_(bd.k_B, 1)
		assert_array_equal(bd.energies, [])
		assert_array_equal(bd.degeneracies, [])
		eq_(bd.num_levels, (0, 0))

		eq_(bd.Z(123), 0)

	def testBeta(self):
		"""
		Check the relationship between k_B, T, and beta.
		"""

		with self.assertRaises(ValueError):
			BoltzmannDistribution(0, [], [])

		for k_B in xrange(1, 10):
			for T in xrange(1, 10):
				bd = BoltzmannDistribution(k_B, [], [])

				assert_almost_equal(k_B * T * bd.beta(T), 1)

	def testSimple(self):
		"""
		Just a regular distribution.
		"""

		bd = BoltzmannDistribution(0.5, [1, 2, 3], [3, 2, 1])

		eq_(list(bd.levels), range(3))
		eq_(bd.k_B, 0.5)
		assert_array_equal(bd.energies, [1, 2, 3])
		assert_array_equal(bd.degeneracies, [3, 2, 1])
		eq_(bd.num_levels, (3, 6))

		assert_array_almost_equal(bd.b_factors(2), [1.103638323514327, 0.270670566473225, 0.049787068367864])
		assert_almost_equal(bd.Z(2), 1.424095958355416)

		# Check the ground state.
		assert_array_equal(bd.ps(0), [1, 0, 0])

		# Check finite temperature.
		assert_array_almost_equal(bd.ps(2), [0.774974689759556, 0.190064837193838, 0.034960473046605])

		assert_almost_equal(bd.energy(2), 1.259985783287049)
		assert_almost_equal(bd.entropy(2), 0.315191678445456)
		assert_almost_equal(bd.heat_capacity(2), 0.131157060934439)

		with self.assertRaises(AttributeError):
			bd.energies = [5]

		with self.assertRaises(AttributeError):
			bd.degeneracies = [5]

	def testOutOfOrder(self):
		"""
		Verify that levels are checked upon creation.
		"""

		with self.assertRaises(ValueError):
			BoltzmannDistribution(1, [1, 2], [1])

		with self.assertRaises(NonIncreasingEnergies):
			BoltzmannDistribution(1, [1, 2, 3, 4, 5, 5], [1] * 6)

		with self.assertRaises(NonIncreasingEnergies):
			BoltzmannDistribution(1, [1, 2, 3, 4, 5, 4], [1] * 6)

	def testFromFile(self):
		"""
		Load from a file.
		"""

		name = 'test1'
		path = join(TEST_DATA, name + '.json')

		bd = BoltzmannDistribution.from_file(path)

		eq_(bd.num_levels, (3, 9))
		eq_(bd.filename, name)


if __name__ == '__main__':
	main()

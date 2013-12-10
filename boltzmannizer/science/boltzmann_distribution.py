from __future__ import division

from json import load
from math import exp, log
from os.path import basename, splitext

import numpy as N

from boltzmannizer.tools.misc import memoized


class InvalidFormat(Exception): pass

class NonIncreasingEnergies(Exception): pass


class BoltzmannDistribution(object):
	"""
	Utilities for working with a Boltzmann distribution of discrete levels of
	known energy and degeneracy.
	"""

	def __init__(self, k_B, energies, degeneracies, units=None, filename=None):
		"""
		k_B should be the Boltzmann constant in units of energy/temperature,
		matching the units for the energies and temperatures.

		Energies are assumed to be in strictly increasing order. If this is
		found not to be the case, a NonIncreasingEnergies exception is raised.

		If the units are specified, they must be in the form of a dict
		containing the keys 'energy' and 'temperature'. These values are used
		for display only.
		"""

		# The results are cached, so these values should not be modified.
		# Read-only properties are provided.
		self._k_B = k_B
		self._energies = N.array(energies)
		self._degeneracies = N.array(degeneracies)

		if self._k_B <= 0:
			raise ValueError('k_B must be positive')

		if len(self._energies) != len(self._degeneracies):
			raise ValueError("Number of energies doesn't match number of degeneracies")

		self.units = units
		self.filename = filename

		# Enforce order.
		for i in xrange(len(self._energies) - 1):
			if self._energies[i] >= self._energies[i+1]:
				raise NonIncreasingEnergies('{0} >= {1}'.format(self._energies[i], self._energies[i+1]))

	@classmethod
	def from_file(cls, path):
		"""
		Load a Boltzmann distribution from a JSON file.

		Any exceptions that might happen due to reading or parsing the file are
		passed through.

		In addition, an InvalidFormat exception may be raised if the contents
		of the file do not make sense.
		"""

		with open(path) as f:
			data = load(f)

		try:
			format_version = data['format_version']
		except KeyError:
			raise InvalidFormat('No format_version specified')

		if format_version != 1:
			raise InvalidFormat('Unable to parse file with format_version: {0}'.format(format_version))

		# Make the filename more presentable by dropping the dirname and extension.
		filename = splitext(basename(path))[0]

		try:
			k_B = data['k_B']
			levels = data['levels']
		except KeyError as exc:
			raise InvalidFormat('Missing data: {0}'.format(exc))

		try:
			units = data['units']

			assert 'energy' in units
			assert 'temperature' in units
		except:
			# Units would be nice to have, but don't complain if something's
			# wrong.
			units = None

		energies = []
		degeneracies = []

		for i, level in enumerate(levels):
			try:
				energies.append(level[0])
			except IndexError:
				raise InvalidFormat('Missing energy in level {0}'.format(i))

			try:
				degeneracies.append(level[1])
			except IndexError:
				# Default degeneracy is 1.
				degeneracies.append(1)

		return cls(k_B, energies, degeneracies, units=units, filename=filename)

	@property
	def k_B(self):
		return self._k_B

	@property
	def energies(self):
		return self._energies

	@property
	def degeneracies(self):
		return self._degeneracies

	@property
	def levels(self):
		"""
		Iterator for the level indices.
		"""

		return xrange(len(self.energies))

	@property
	def num_levels(self):
		"""
		Number of levels and number of states.
		"""

		return len(self.degeneracies), sum(self.degeneracies)

	@memoized
	def beta(self, T):
		"""
		Value of beta for the given temperature.

		$\\beta = \\frac{1}{k_B T}$

		Temperature is assumed to be positive.
		"""

		return 1 / (self.k_B * T)

	@memoized
	def b_factors(self, T):
		"""
		Boltzmann factors of all the levels at temperature T.

		$g_i e^{-\\beta E_i}$
		"""

		return self.degeneracies * N.exp(-self.beta(T) * self.energies)

	@memoized
	def Z(self, T):
		"""
		Value of the partition function for some temperature.

		$Z = \\sum_{i=1}^n g_i e^{-\\beta E_i}$
		"""

		return self.b_factors(T).sum()

	@memoized
	def ps(self, T):
		"""
		Probabilities of occupying the levels at temperature T.

		$p_i = \\frac{1}{Z} g_i e^{-\\beta E_i}$
		"""

		if T == 0:
			# Treat the zero-temperature case explicitly, assuming that
			# everything is in the ground state.
			return self._ground_state_ps
		else:
			Z = self.Z(T)

			if Z == 0.0:
				# If Z is zero, also assume that we're in the ground state,
				# because we're probably here due to rounding error at very low
				# temperature.
				return self._ground_state_ps

			return self.b_factors(T) / Z

	@memoized
	def energy(self, T):
		"""
		Internal energy at temperature T.

		$U = \\langle E \\rangle = \\frac{1}{Z} \\sum_{i=1}^n E_i g_i e^{-\\beta E_i}$
		"""

		return (self.energies * self.ps(T)).sum()

	@memoized
	def entropy(self, T):
		"""
		Gibbs entropy at temperature T.

		$S = -k_B \\sum_{i=1}^n p_i \\ln{p_i}$

		Has the same units as k_B.
		"""

		ps_all = self.ps(T)
		# By convention, 0 log 0 = 0, so we can drop those.
		ps = ps_all[ps_all.nonzero()]

		return -self.k_B * (ps * N.log(ps)).sum()

	@memoized
	def heat_capacity(self, T):
		"""
		Heat capacity (at constant volume) at temperature T.

		$C_V = \\frac{\\beta}{T} \\langle (\\Delta E)^2 \\rangle$

		Has the same units as k_B.

		Temperature is assumed to be positive.
		"""

		return self.beta(T) * (self._energy_sq(T) - self.energy(T) * self.energy(T)) / T

	@property
	def _ground_state_ps(self):
		result = N.zeros(self.num_levels[0])
		result[0] = 1.0

		return result

	@memoized
	def _energy_sq(self, T):
		"""
		Expectation value of the square of the energy at temperature T.

		$\\langle E^2 \\rangle = \\frac{1}{Z} \\sum_{i=1}^n E_i^2 g_i e^{-\\beta E_i}$

		Not the same as squaring the result of energy(), as that quantity would
		be the square of the expectation value of the energy instead.
		"""

		return (self.energies ** 2 * self.ps(T)).sum()

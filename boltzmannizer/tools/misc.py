from functools import wraps


def memoized(f):
	"""
	A simple memoization decorator.
	"""

	cache = f.cache = {}

	@wraps(f)
	def wrapper(*args, **kwargs):
		key = (args, frozenset(kwargs.items()))

		if key in cache:
			return cache[key]

		result = f(*args, **kwargs)
		cache[key] = result

		return result

	return wrapper

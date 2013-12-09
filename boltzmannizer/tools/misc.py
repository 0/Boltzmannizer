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


class Reserver(object):
	"""
	Manage reservations of some objects, trying to assign the "better" objects
	first.
	"""

	def __init__(self, objs, overflow_obj):
		"""
		objs: List of objects to be reserved.
		overflow_obj: The object to use once objs is depleted.

		The elements of objs are assumed to be sorted so that earlier objects
		are preferred over later ones.
		"""

		self._objs = objs
		self._overflow_obj = overflow_obj

		self.assigned_objs = [False] * self.num_objs

	@property
	def num_objs(self):
		return len(self._objs)

	def allocate(self):
		for i, obj in enumerate(self._objs):
			if not self.assigned_objs[i]:
				self.assigned_objs[i] = True

				return obj

		# Contingency plan!
		return self._overflow_obj

	def free(self, obj_free):
		if self._overflow_obj == obj_free:
			# Nothing to be done about this.
			return

		for i, obj in enumerate(self._objs):
			if obj == obj_free:
				# Don't worry about freeing unassigned objects.
				self.assigned_objs[i] = False

				return

		raise ValueError('Not a valid object: {0}'.format(obj_free))

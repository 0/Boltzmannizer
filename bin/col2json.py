#!/usr/bin/env python2

"""
Convert column-based data into the JSON format used by the Boltzmannizer.
"""

from argparse import ArgumentParser
import fileinput


# Parse the arguments.
parser = ArgumentParser()
parser.add_argument('energies', type=int, help='one-based index of the energies column')
parser.add_argument('degeneracies', type=int, help='one-based index of the degeneracies column')

args = parser.parse_args()

# Convert to zero-based.
col_energies = args.energies - 1
col_degeneracies = args.degeneracies - 1


# Collect the data.
energies = []
degeneracies = []

for line in fileinput.input('-'):
	cols = line.split()

	if not cols:
		# Skip empty lines.
		continue

	e, d = cols[col_energies], cols[col_degeneracies]

	if energies and e == energies[-1]:
		# Combine degenerate levels.
		degeneracies[-1] = str(int(degeneracies[-1]) + int(d))
	else:
		energies.append(e)
		degeneracies.append(d)


# Output the JSON file.
#
# Not using a serializer here to preserve the order and shape of the output.
# The units are hard-coded for the time being, but it doesn't need to be that
# way.
print '''{ "format_version": 1
, "k_B": 0.695031
, "units": { "energy": "cm^-1"
           , "temperature": "K"
           }
, "levels": [''',

first = True

for e, d in zip(energies, degeneracies):
	if not first:
		print '            ,',
	else:
		first = False

	print '[{0}, {1}]'.format(e, d)

print '            ]'
print '}'

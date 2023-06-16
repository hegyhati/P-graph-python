import os
import sys

os.chdir(sys.argv[1])

for f in os.listdir():
	if f[-4:] == ".out":
		with open(f) as ff:
			for line in ff:
				print(line.strip(), end=' ')

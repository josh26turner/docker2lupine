import sys

from statistics import mean, pvariance

vals = []

for line in sys.stdin:
    vals.append(float(line))

print(str(round(mean(vals), 4)) + ',' + str(round(pvariance(vals) ** 0.5, 4)))
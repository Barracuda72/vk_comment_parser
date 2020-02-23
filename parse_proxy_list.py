#!/usr/bin/env python

import csv
import sys

if (len(sys.argv) < 2):
    print("Pass proxy CSV file!")
    sys.exit(0)

with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile)
    # Skip title
    next(reader)
    for row in reader:
        line = "{}://{}:{}".format(row[2], row[0], row[1]).lower()
        print (line)

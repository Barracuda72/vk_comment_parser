#!/usr/bin/env python3

import sys

if (len(sys.argv) < 2):
    print ("Provide file with IDs!")
    sys.exit(1)

filename = sys.argv[1]

user_ids = [x.strip() for x in open(filename, "r").readlines()]

p = Populator()

for user_id in user_ids:
    message = "{} {}".format(user_id, 0)
    p.populate_work(message)

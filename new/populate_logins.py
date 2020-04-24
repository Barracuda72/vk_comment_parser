#!/usr/bin/env python3

import sys

from Populator import Populator

if (len(sys.argv) < 2):
    print ("Provide file with IDs!")
    sys.exit(1)

filename = sys.argv[1]

vk_credentials = [x.strip() for x in open(filename, "r").readlines()]

p = Populator()

for message in vk_credentials:
    p.publish_login(message)

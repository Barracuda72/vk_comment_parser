#!/usr/bin/env python

import random
import time

import requests
import bs4 as bs

proxies = {
  "http": "socks5://127.0.0.1:9050",
  "https": "socks5://127.0.0.1:9050",
}

while True:
    prefix = random.randint(0, 5843980)
    prefix_str = "{}-{}-{}".format(prefix // 10000, prefix % 10000 // 100, prefix % 100)

    url = "https://vk.com/catalog.php?selection={}".format(prefix_str)

    r = requests.get(url, proxies=proxies)

    if (r.status_code != 200):
        continue

    soup = bs.BeautifulSoup(r.text, "lxml")

    divs = soup.find_all("div", {'class' : "column2"})

    ids = [x['href'] for y in divs for x in y.find_all("a")]

    ids = [x.replace("id", "") for x in ids]

    for i in ids:
        print (i)

    time.sleep(1)

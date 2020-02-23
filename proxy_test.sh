#!/bin/sh

proxy_list=$1

host="https://semograph.org"

temp_file=`mktemp`

jobs=10

rm ${temp_file}

python3 parse_proxy_list.py ${proxy_list} > ${temp_file}

cat ${temp_file} | parallel -j ${jobs} --tag curl --proxy {} -o /dev/null --silent --head --write-out  '%{http_code}' ${host} --max-time 50 | grep 200 > verified_proxies.txt

rm ${temp_file}

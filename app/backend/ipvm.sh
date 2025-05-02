#!/bin/bash
ip=$(virsh domifaddr --source arp $1 | grep /0 | tr "/" " " | tr " " '\n')

for li in $ip
ip2=""
do
if [[ "$li" =~ 192.* ]] ; then
ip2="$li"
fi

done
echo "$ip2"



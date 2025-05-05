#!/bin/bash
hosts=$(cat /etc/hosts)
rm /etc/hosts.tmp
touch /etc/hosts.tmp
while read -r li
do
    echo $li
    if [[ "$li" =~ 192.* ]]; then
        if [[ ! "$li" =~  $1$ ]]; then
            echo $li >> /etc/hosts.tmp
        fi
    else
        echo $li >> /etc/hosts.tmp
    fi
done < "/etc/hosts"

rm /etc/hosts
cp /etc/hosts.tmp /etc/hosts
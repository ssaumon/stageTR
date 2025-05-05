#!/bin/bash
hosts=$(cat /etc/hosts)
echo "" > /etc/hosts.tmp
while read -r li
do
    echo $li
    if [[ "$li" =~ "192.*" ]]; then
        if [[ ! "$li" =~ " $1$" ]]; then
            echo $li >> /etc/hosts.tmp
            echo $li
        fi
    else
        echo $li >> /etc/hosts.tmp
        echo "oui"
    fi
done < "/etc/hosts"

rm /etc/hosts
cp /etc/hosts.tmp /etc/hosts
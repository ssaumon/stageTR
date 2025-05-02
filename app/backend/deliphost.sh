hosts=$(cat /etc/hosts)
newhosts=""
for $li in $hosts
do
    if [["$li" =~ '192.*']]; then
        if [[ ! "$li" =~ " $1 "]];then
            newhosts+="$li\n"
        fi
    else
        newhosts+="$li\n"
    fi
done

echo $newhosts > /etc/hosts
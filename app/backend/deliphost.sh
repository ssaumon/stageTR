hosts=$(cat /etc/hosts)
newhosts=""
while read -r li
do
    if [[ "$li" =~ '192.*' ]]; then
        if [[ ! "$li" =~ " $1 " ]]; then
            newhosts+="$li\n"
        fi
    else
        newhosts+="$li"$'\n'
    fi
done < "/etc/hosts"

echo $newhosts > /etc/hosts
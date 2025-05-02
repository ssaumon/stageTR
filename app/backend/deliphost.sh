hosts=$(cat /etc/hosts)
echo "" > /etc/hosts
while read -r li
do
    echo $li
    if [[ "$li" =~ '192.*' ]]; then
        if [[ ! "$li" =~ " $1 " ]]; then
            echo $li >> /etc/hosts
        fi
    else
        echo $li >> /etc/hosts
    fi
done < "/etc/hosts"

#!/bin/bash
input="./layers.properties"

HOUR=3600 #secs in 1 hour
now_epoch=$(date +%s)
date -d @$now_epoch | xargs echo "Starting cleaning process with time = "

path_slashes=$(echo "${1}" | awk -F"/" '{print NF-1}')
let path_depth=$path_slashes+2

echo "..."
if [ -f "$input" ]
then
  echo "Layers retention time properties file: $input found."
  echo "..."
  # outer while: reading each layer retention time setting (granularity: hours)
  while IFS='=' read -r key value
  do
    #eval ${key}=\${value}
    # inner while: 
    echo "Cleaning cache for layer: $key - Retention time: $value hours"
    let diff_epoch=$now_epoch-$value*$HOUR
    date -d @$diff_epoch | xargs echo "Checking cache folders with TIME dimension previous to "
    find ${1} -type d -name $key -print0 | 
    while IFS= read -r -d '' line; do 
        echo "   Found folder to review: $line"
        folder_time_dimension_epoch=$(echo $line | sed -r 's/[#]+/_/g' | cut --delimiter="/" -f${path_depth} | cut --delimiter="_" -f3 | xargs -I{} date -d {} +%s)
        if [ ! -z "${folder_time_dimension_epoch}" ] 
        then
           if [ $folder_time_dimension_epoch -lt $diff_epoch ]
           then
             echo "   --> Deleting folder $line"
             rm -rdf $line
           fi
        fi
    done
    echo "..."
  done < "$input"
else
  echo "Layers retention time properties file $file not found."
fi

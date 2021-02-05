#!/bin/bash

#######################################################################################
#
# Clean mapcache folders based on "time-dimension/layer-tiles" structure folder.
# Parse the time-dimension folder name getting the time.
# Compares with retetion time defined for each folder (in layers.properties file)
# If retention time defeats, then remove the layer-tiles folder.
# 
#######################################################################################

input=${2}

HOUR=3600 #secs in 1 hour
now_epoch=$(date +%s)
echo "----------------------------------------------------------------------"
date -d @$now_epoch | xargs echo "Starting cleaning process with time = "
echo "Cache root folder = $1"

path_slashes=$(echo "${1}" | awk -F"/" '{print NF-1}')
let path_depth=$path_slashes+2

echo "..."
if [ -f "$input" ]
then
  echo "Layers retention time properties file: $input found."
  # outer while: reading each layer retention time setting (granularity: hours)
  while IFS='=' read -r key value
  do
    # inner while: 
    echo "..."
    echo "Cleaning cache for layer: $key - Retention time: $value hours"
    let diff_epoch=$now_epoch-$value*$HOUR
    date -d @$diff_epoch | xargs echo "Checking cache folders with TIME dimension previous to "
    echo "..."
    find ${1} -maxdepth 2 -type d -name $key -print0 | 
    while IFS= read -r -d '' line; do 
        echo "   Folder in revision: $line"
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
  done < "$input"
else
  echo "Layers retention time properties file $file not found."
fi
echo "----------------------------------------------------------------------"
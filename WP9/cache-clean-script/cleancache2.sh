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

caller=$(pwd)

path_slashes=$(echo "${1}" | awk -F"/" '{print NF-1}')
let path_depth=$path_slashes+2
declare -A retention_times=()

echo "..."
if [ -f "$input" ]
then
  echo "Layers retention time properties file: $input found."
  # reading each layer retention time setting (granularity: hours)
  # adding them to associative array (key is the retention_time)
  while IFS='=' read -r layer value
  do
    retention_times[$value]+=" ./$layer/"
  done < "$input"
  # outer while: for each folder in cache (time dimension level)
  for folder in ${1}/*; do
    #echo "Checking folder -> $folder"
    folder_time_dimension_epoch=$(echo $folder | sed -r 's/[#]+/_/g' | cut --delimiter="/" -f${path_depth} | cut --delimiter="_" -f3 | xargs -I{} date -d {} +%s)
    # inner while: check if any retention_time is applicable, if so, remove layers folder level
    for retKey in "${!retention_times[@]}"; do 
      let value=$retKey
      let diff_epoch=$now_epoch-$value*$HOUR
      if [ ! -z "${folder_time_dimension_epoch}" ] 
      then
        if [ $folder_time_dimension_epoch -lt $diff_epoch ]
        then
          echo "   --> Deleting layers folders from time-dimension $folder with retkey > $retKey"
          echo "   --> Layers: ${retention_times[$retKey]}"
          cd $folder
          rm -rdf ${retention_times[$retKey]}
          cd $caller
        fi
      fi
    done
  done

else
  echo "Layers retention time properties file $file not found."
fi
echo "----------------------------------------------------------------------"
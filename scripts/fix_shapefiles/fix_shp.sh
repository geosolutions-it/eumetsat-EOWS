#!/bin/bash

for item in *.shp
do
echo $item;
./wms_shape_fix.py $item output/$item
done



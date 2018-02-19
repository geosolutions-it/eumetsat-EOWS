#!/bin/bash

for item in *.nc
do
echo $item;

cp $item in_progress/to_be_processed.nc
java -Xmx2g -classpath ./processing/netcdfAll-4.6.11.jar ucar.nc2.dataset.NetcdfDataset -in in_progress/ghrsst.ncml -out in_progress/all_float.nc
if [ -f in_progress/all_float.nc ]; then
   FILESIZE=`du --apparent-size --block-size=1 in_progress/all_float.nc`
   echo "File in_progress/all_float.nc exists with size: $FILESIZE"
   echo "Recompressing with netcdf4"
   java -Xmx2g -classpath ./processing/netcdfAll-4.6.11.jar ucar.nc2.dataset.NetcdfDataset -in in_progress/3to4.ncml -out in_progress/finale4.nc -netcdf4
   if [ -f in_progress/finale4.nc ]; then
      FILESIZE=`du --apparent-size --block-size=1 in_progress/finale4.nc`
      echo "File in_progress/finale4.nc exists with size: $FILESIZE"
      mv in_progress/finale4.nc output/$item
      rm in_progress/all_float.nc
   else
      echo "Error processing into NETCDF4"
   fi
else
   echo "File does not exist!"
fi

done


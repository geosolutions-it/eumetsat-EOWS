#!/bin/bash

for item in input/*.nc
do
echo $item;

cp $item workspace/in_progress.nc
java -Xmx2g -classpath ./tools/netcdfAll-4.6.11.jar ucar.nc2.dataset.NetcdfDataset -in tools/sosi.ncml -out workspace/all_float_nc3.nc
if [ -f workspace/all_float_nc3.nc ]; then
   # FILESIZE=`du --apparent-size --block-size=1 workspace/all_float_nc3.nc`
   # echo "File workspace/all_float_nc3.nc exists with size: $FILESIZE"
   echo "Recompressing with netcdf4"
   mv workspace/all_float_nc3.nc workspace/in_progress.nc
   java -Xmx2g -classpath ./tools/netcdfAll-4.6.11.jar ucar.nc2.dataset.NetcdfDataset -in tools/sosi.ncml -out output/${item##*/} -netcdf4
   if [ -f output/${item##*/} ]; then
      # FILESIZE=`du --apparent-size --block-size=1 output/${item##*/}`
      # echo "File output/${item} exists with size: $FILESIZE"
      rm workspace/all_float_nc3.nc
	  rm workspace/in_progress.nc
   else
      echo "Error processing into NETCDF4"
   fi
else
   echo "File does not exist!"
fi

done

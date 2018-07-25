# How to prepare GHRSST NETCDF files for import (S-OSI_-FRA_-MTOP-GLBSST_FIELD)

GeoServer does not currently supports coverage views from a mosaic with non-omogeneous variables types.
The GHRSST-compliant files must be fixed to have all float variables.

This script is for Bash

## Requirements

* Java 7 or later
* [NetCDF-Java](https://artifacts.unidata.ucar.edu/repository/unidata-releases/edu/ucar/netcdfAll/4.6.11/netcdfAll-4.6.11.jar)
* [NetCDF4 native library](https://www.unidata.ucar.edu/software/thredds/current/netcdf-java/reference/netcdf4Clibrary.html)

## Steps

1. Put all the NetCDF files to be converted in the "input" folder
1. Put the netcdfAll-4.6.11.jar in the "tools" folder
1. Run ./process.sh (it will create the fixed netcdf files in the "output" folder)


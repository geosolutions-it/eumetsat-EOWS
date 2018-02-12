# How to prepare ASCAT Shapefiles for import

The Shapefiles must be fixed and compressed.

## Requirements

* Python 2
* pip
* PySHP (pip install pyshp)

## Steps

1. Put all the Shapefiles to be converted in the same folder
1. Copy fix_shp.sh and wmx_shp_fix.py in it
1. Create an "output" folder inside it
1. Run ./fix_shp.sh (it will create the fixed shapefiles in the "output" folder)
1. `cd output`
1. Run the following comands to zip all the output files
   * `declare -A prefixes`
   * `for f in *; do prefixes[${f%%.*}]=1; done`
   * `for p in "${!prefixes[@]}"; do zip "$p" "$p".*; done`


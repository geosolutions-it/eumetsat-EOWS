#!/usr/bin/python

import sys, getopt
import shapefile

def convert(input, output=None):
    if output is None:
        output = input
    print "Open shapefile: " + input
    sf = shapefile.Reader(input)

    print "Converting fields: " + str(sf.fields[1:])
    fields = sf.fields[1:]

    fieldsNew = []
    for field in fields:
        lst = list(field)
        lst[0] = lst[0].lower().replace(" ", "_")
        fieldsNew.append(tuple(lst))

    print "Converted to " + str(fieldsNew)
    w = shapefile.Writer()
    w.fields = fieldsNew

    print "Copy shape attributes..."
    for shaperec in sf.iterShapeRecords():
        w.record(*shaperec.record)
        w.point(shaperec.shape.points[0][0], shaperec.shape.points[0][1])

    print "Save file to: " + output
    w.save(output)


if __name__ == "__main__":
   convert(sys.argv[1], sys.argv[2])

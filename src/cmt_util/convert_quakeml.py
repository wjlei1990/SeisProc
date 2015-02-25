# convert quakeml file into CMTSOLUTION file

from source import CMTSource
from obspy import readEvents
import glob
import os

quakemldir = "/home/lei/DATA/quakeml"
outputdir = "/home/lei/DATA/CMT_BIN/from_quakeml"

search_pattern = os.path.join(quakemldir, "*.xml")
quakemllist = glob.glob(search_pattern)

if not os.path.exists(outputdir):
    os.mkdir(outputdir)

print "Total number of quakeml files:", len(quakemllist)

for _idx, quakeml in enumerate(quakemllist):
    cmt = CMTSource.from_quakeml_file(quakeml)
    filename = cmt.eventname
    outputpath = os.path.join(outputdir, filename)
    print _idx, filename, outputpath
    cmt.write_CMTSOLUTION_file(outputpath)


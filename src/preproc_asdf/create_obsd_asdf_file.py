import glob
import os
from convert_util import convert_asdf

eventname = "201302091416A"
filetype = "mseed"

basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/OBSD/waveforms"
quakemldir = "/ccs/home/lei/EVENT_CENTER/quakeml"
staxmlbasedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/OBSD/stationxml"

tag = "raw_observed"

output_fn = eventname + "_" + tag  + ".h5"

# data list
datadir = os.path.join(basedir, eventname)
search_pattern = os.path.join(datadir, "*"+filetype)
filelist = glob.glob(search_pattern)

# stationxml
staxmldir = os.path.join(staxmlbasedir, eventname)
search_pattern = os.path.join(staxmldir, "*.xml")
staxml_list = glob.glob(search_pattern)
print "SP:", search_pattern
print "Number of Statoinxml found:", len(staxml_list)

# Quakeml file
quakemlfile = os.path.join(quakemldir, "%s.xml" %eventname)
if not os.path.exists(quakemlfile):
    raise IOError("Not Quakemlfile for this event %s" %eventname)

print "="*20
print "Search Pattern:", search_pattern
print "Total number of files:", len(filelist)
print "Output filename:", output_fn

if os.path.exists(output_fn):
    print "Outfile exist and being removed:", output_fn
    os.remove(output_fn)

if len(filelist) >= 0:
    convert_asdf(filelist, output_fn, quakemlfile, staxml_list, tag=tag)

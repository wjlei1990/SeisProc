import glob
import os
from convert_util import convert_asdf

eventname = "010403A"
filetype = "sac"

basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/SYNT/temp/data"
quakemldir = "/ccs/home/lei/EVENT_CENTER/quakeml"
staxmlbasedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/OBSD/stationxml"
outputdir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/raw"

tag = "raw_synthetic"

type_list = ["", "Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp", "dep", "lon", "lat"]
#type_list = ["", "dep", "lon", "lat"]
#type_list = ["",]

# stationxml
staxmldir = os.path.join(staxmlbasedir, eventname)
search_pattern = os.path.join(staxmldir, "*.xml")
staxml_list = glob.glob(search_pattern)
print "Stationxml file..."
print "SP:", search_pattern
print "Number of Statoinxml found:", len(staxml_list)

# Quakeml file
quakemlfile = os.path.join(quakemldir, "%s.xml" %eventname)
if not os.path.exists(quakemlfile):
    raise IOError("Not Quakemlfile for this event %s" %eventname)
print "Quakeml file: %s" % quakemlfile

for type in type_list:
    print "="*20
    print "type:", type
    if type == "":
        datadirbase = eventname
    else:
        datadirbase = eventname + "_" + type
    datadir = os.path.join(basedir, datadirbase)
    search_pattern = os.path.join(datadir, "OUTPUT_FILES", "*"+filetype)
    filelist = glob.glob(search_pattern)

    print "Search Pattern:", search_pattern
    print "Total number of files:", len(filelist)

    if type == "":
        output_fn = eventname + "." + tag  + ".h5"
    else:
        output_fn = eventname + "." + type + "." + tag  + ".h5"

    output_fn = os.path.join(outputdir, output_fn)
    print "Output filename:", output_fn

    if os.path.exists(output_fn):
        print "Outfile exist and being removed:", output_fn
        os.remove(output_fn)

    if len(filelist) >= 0:
        convert_asdf(filelist, output_fn, quakemlfile, staxml_list, tag=tag)

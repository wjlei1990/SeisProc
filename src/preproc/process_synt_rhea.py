from obspy import read, read_inventory, readEvents
from obspy.core.util.geodetics import gps2DistAzimuth
import time
import glob
import os
import re
from synt_util import *
import sys

if len(sys.argv) != 4:
    raise ValueError("Incorrect arg number")

eventname = sys.argv[1]
# set the filter band
period_band = [int(sys.argv[2]), int(sys.argv[3])]

# Rhea
basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI"
quakemldir = "/ccs/home/lei/SOURCE_INVERSION/quakeml" 
stationxml_dir = os.path.join(basedir, "OBSD", "stationxml")
outputbase = os.path.join(basedir, "SYNT_PROC")
#database = "/lustre/atlas/scratch/lei/geo111/SOURCE_INVERSION/run_scripts/job_shallow_39/data"
database = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/SYNT/temp/data"

datadir = os.path.join(database, eventname)

# event
eventfile = os.path.join(quakemldir, "%s.xml" %eventname)
cat = readEvents(eventfile)
event = cat.events[0]
event_time = event.preferred_origin().time
print "Event time:", event_time


#output dir
event_name = get_event_name(event)
event_name = adjust_event_name(event_name)
output_dir = event_name + "_" + str(period_band[0]) + "_" + str(period_band[1])
output_dir = os.path.join(outputbase, output_dir)

# npts and sampling rate in iterpolation
npts = 3600
sampling_rate = 1.0

# processing
t1 = time.time()
# data filename
#suffix_list = [ "", "Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp", "lon", "lat", "dep"]
suffix_list = ["", ]

print "Summary:"
print "datadir:", datadir
print "stationxml_dir:", stationxml_dir
print "outputdir:", output_dir


for suffix in suffix_list:
    print suffix
    if suffix != "":
        ddir = datadir + "_" + suffix
    else:
        ddir = datadir
    ddir=os.path.join(ddir, "OUTPUT_FILES")
    stationlist=generate_station_list(ddir)
    #stationlist = [stationlist[0],]
    #print stationlist
    for station in stationlist:
        #print station
        process_synt(ddir, station, event, stationxml_dir, period_band, npts, sampling_rate, output_dir, suffix=suffix)

t2 = time.time()
print "Total time:", t2-t1

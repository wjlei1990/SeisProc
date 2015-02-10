from obspy import read, read_inventory, readEvents
from obspy.core.util.geodetics import gps2DistAzimuth
import time
import glob
import os
import re
from synt_util import *

# Rhea
#quakemldir = "/ccs/home/lei/SOURCE_INVERSION/quakeml/cmt_deep_events/quakeml"
#stationxml_dir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_PROCESS/OBSD/deep_events/stationxml"
#outputbase = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_PROCESS/OBSD_PROC"
#database = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_PROCESS/OBSD/deep_events/waveforms"

# local machine
basedir = "/home/lei/Research/SOURCE_INVERSION/DATA"
quakemldir = os.path.join(basedir, "Quakeml")
stationxml_dir = os.path.join(basedir, "stationxml")
outputbase = os.path.join(basedir, "SYNT_PROC")
database = os.path.join(basedir, "SYNT")

eventname = "010104J"

datadir = os.path.join(database, eventname)

# event
eventfile = os.path.join(quakemldir, "%s.xml" %eventname)
cat = readEvents(eventfile)
event = cat.events[0]
event_time = event.preferred_origin().time
print "Event time:", event_time

# set the filter band
period_band = [60, 120]

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
#suffix_list = [ "Mpp", "Mrt", "Mrp", "Mtp"]
suffix_list = ["", ]

print "Summary:"
print "datadir:", datadir
print "stationxml_dir:", stationxml_dir
print "outputdir:", output_dir


for suffix in suffix_list:
    print suffix
    if suffix != "":
        datadir = datadir + "_" + suffix
    datadir=os.path.join(datadir, "OUTPUT_FILES")
    stationlist=generate_station_list(datadir)
    #stationlist = [stationlist[0],]
    #print stationlist
    for station in stationlist:
        #print station
        process_synt(datadir, station, event, stationxml_dir, period_band, npts, sampling_rate, output_dir, suffix=suffix)

t2 = time.time()
print "Total time:", t2-t1
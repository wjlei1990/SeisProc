from obspy import read, read_inventory, readEvents
from obspy.core.util.geodetics import gps2DistAzimuth
import time
import glob
import os
import re
from data_util import *
import sys

if len(sys.argv) != 4:
    raise ValueError("Incorrect arg number")

eventname = sys.argv[1]
# set the filter band
period_band = [int(sys.argv[2]), int(sys.argv[3])]

# rhea
basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI"
quakemldir = "/ccs/home/lei/SOURCE_INVERSION/quakeml"
stationxml_dir = os.path.join(basedir, "OBSD", "stationxml")
outputbase = os.path.join(basedir, "OBSD_PROC")
database = os.path.join(basedir, "OBSD", "waveforms")

# event
eventfile = os.path.join(quakemldir, "%s.xml" %eventname)
print "Quakeml file:", eventfile

if not os.path.isfile(eventfile):
    raise ValueError("Event file not exist")

cat = readEvents(eventfile)
event = cat.events[0]

#output dir
event_name = get_event_name(event)
event_name = adjust_event_name(event_name)
output_dir = event_name + "_" + str(period_band[0]) + "_" + str(period_band[1])
output_dir = os.path.join(outputbase, output_dir)

# data dir
datadir = os.path.join(database, event_name)

print "output dir:", output_dir
print "datadir:", datadir

# npts and sampling rate in iterpolation
npts = 3600
sampling_rate = 1.0

# processing
t1 = time.time()
# data filename

filelist = glob.glob(datadir+"/*.mseed")
print "Total number of file:", len(filelist)

#process_data(datafile, event, stationxml_dir, period_band, npts, sampling_rate, output_dir)
for datafile in filelist:
    process_data(datafile, event, stationxml_dir, period_band, npts, sampling_rate, output_dir)
#datafile = "../OBSD/010104J/IC.ENH.mseed"
#process_data(datafile, event, stationxml_dir, period_band, npts, sampling_rate, output_dir)

t2 = time.time()
print "Total time:", t2-t1

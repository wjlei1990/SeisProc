from plot_azi_util import *
import os
import glob

quakemldir="/u/lei/Research/SOURCE_INVERSION/quakeml"
winfiledir="./data"
tag=["35_60", "60_120"]
event_list=["010202E",]
stationfile = "./data/STATIONS"

for event in event_list:
    quakemlfile = os.path.join(quakemldir, event)
    winfilelist = [ "%s_%s.win" %(event, x) for x in tag ]
    winfile = [ os.path.join(winfiledir,x) for x in winfilelist ]
    print quakemlfile
    print winfile
    plot_window_azi(winfile, quakemlfile, stationfile)
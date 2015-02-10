from obspy import read
import matplotlib.pyplot as plt
import obspy
import pyflex
import numpy as np
import os
import glob
import sys

basedir = "/home/lei/Research/SOURCE_INVERSION/DATA"
databasedir = os.path.join(basedir, "OBSD_PROC")
syntbasedir = os.path.join(basedir, "SYNT_PROC")
outputbasedir = os.path.join(basedir, "window")

event = "010104J"
period_band = [27, 60]
eventdir = "%s_%d_%d" % (event, min(period_band), max(period_band))

datadir = os.path.join(databasedir, eventdir)
syntdir = os.path.join(syntbasedir, eventdir)
outputdir = os.path.join(outputbasedir, eventdir)

if not os.path.exists(outputdir):
    os.makedirs(outputdir)
figdir = os.path.join(outputdir, "figures")
if not os.path.exists(figdir):
    os.makedirs(figdir)

config_bw = pyflex.Config(
    min_period=27.0, max_period=60.0,
    stalta_waterlevel=0.10, tshift_acceptance_level=10.0,
    dlna_acceptance_level=0.80, cc_acceptance_level=0.80, s2n_limit=2.0,
    check_global_data_quality=True,
    c_0=0.7, c_1=2.0, c_2=0.0, c_3a=1.0, c_3b=2.0, c_4a=3.0, c_4b=10.0)

config_sw = pyflex.Config(
    min_period=60.0, max_period=120.0,
    stalta_waterlevel=0.10, tshift_acceptance_level=18.0,
    dlna_acceptance_level=0.80, cc_acceptance_level=0.80, s2n_limit=2.0,
    check_global_data_quality=True,
    c_0=0.7, c_1=3.0, c_2=0.0, c_3a=1.0, c_3b=2.0, c_4a=3.0, c_4b=10.0,
    window_signal_to_noise_type="amplitude")

if (max(period_band)<65):
    print "Body wave config"
    #body wave(short period)
    config = config_bw
else:
    print "Surface wave config"
    #surface wave(long period)
    config = config_sw

print datadir
print syntdir
print len(glob.glob(datadir + "/*.sac"))
print len(glob.glob(syntdir + "/*.sac"))

for datafile in glob.glob(datadir + "/*.sac"):
    # print datafile
    print "===================\nObsd file:", datafile
    data = read(datafile)
    sta = data[0].stats.station
    nw = data[0].stats.network
    comp = data[0].stats.channel
    loc = data[0].stats.location
    syntfile = sta+"."+nw+".MX"+comp[-1:]+".sac"
    syntfile = os.path.join(syntdir, syntfile)
    if os.path.exists(syntfile):
        print "Synt file:", syntfile
        synt = read(syntfile)
        ws = pyflex.WindowSelector(data, synt, config)
        windows = ws.select_windows()
        # output fig
        outfn = sta + "." + nw + "." + loc + ".MX" + comp[-1:] + ".png"
        figfn = os.path.join(figdir, outfn)
        print "Output fig:", figfn
        ws.plot(figfn)
        # output win
        outfn = sta + "." + nw+ "." + loc + ".MX" + comp[-1:] + ".win"
        winfn = os.path.join(outputdir, outfn)
        print "Output win:", winfn
        ws.write_text(winfn)
    else:
        print "Synt file not exists..."
import pyflex
from pyasdf import ASDFDataSet
import os
import glob
import time
import sys
import copy

eventname = "010202E"
basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/proc"
period = [60, 120]
outputdir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/window"

obsd_tag = "proc_obsd_%d_%d" % (period[0], period[1])
synt_tag = "proc_synt_%d_%d" % (period[0], period[1])

obsd_fn = "%s.%s.h5" %(eventname, obsd_tag)
synt_fn = "%s.%s.h5" %(eventname, synt_tag)
obsd_fn = os.path.join(basedir, obsd_fn)
synt_fn = os.path.join(basedir, synt_fn)

if not os.path.exists(obsd_fn):
    raise ValueError("No obsd file: %s" %obsd_fn)
if not os.path.exists(synt_fn):
    raise ValueError("No synt file: %s" %synt_fn)

obsd_ds = ASDFDataSet(obsd_fn)
synt_ds = ASDFDataSet(synt_fn)
print obsd_ds
print synt_ds

# event information
event = obsd_ds.events[0]

#config_bw = pyflex.Config(
#    min_period=float(period[0]), max_period=float(period[1]),
#    stalta_waterlevel=0.10, tshift_acceptance_level=10.0,
#    dlna_acceptance_level=0.80, cc_acceptance_level=0.80, s2n_limit=2.0,
#    check_global_data_quality=True,
#    c_0=0.7, c_1=2.0, c_2=0.0, c_3a=1.0, c_3b=2.0, c_4a=3.0, c_4b=10.0)

config_bw = pyflex.Config(
    min_period=float(period[0]), max_period=float(period[1]),
    stalta_waterlevel=0.10, tshift_acceptance_level=10.0,
    dlna_acceptance_level=0.80, cc_acceptance_level=0.80, s2n_limit=2.0,
    check_global_data_quality=True,
    c_0=0.7, c_1=2.0, c_2=0.0, c_3a=1.0, c_3b=2.0, c_4a=3.0, c_4b=10.0,
    window_signal_to_noise_type="amplitude")

config_sw = pyflex.Config(
    min_period=float(period[0]), max_period=float(period[1]),
    stalta_waterlevel=0.10, tshift_acceptance_level=18.0,
    dlna_acceptance_level=0.80, cc_acceptance_level=0.80, s2n_limit=2.0,
    check_global_data_quality=True,
    c_0=0.7, c_1=3.0, c_2=0.0, c_3a=1.0, c_3b=2.0, c_4a=3.0, c_4b=10.0,
    window_signal_to_noise_type="amplitude")

if max(period) < 65.0:
    config_base = config_bw
else:
    config_base = config_sw

def window_func(this_station_group, other_station_group):
    # Make sure everything thats required is there.
    if not hasattr(this_station_group, "StationXML") or \
            not hasattr(this_station_group, obsd_tag) or \
            not hasattr(other_station_group, synt_tag):
        print "No attr, return"
        return

    stationxml = this_station_group.StationXML
    observed = getattr(this_station_group, obsd_tag)
    synthetic = getattr(other_station_group, synt_tag)

    all_windows = []

    for component in ["Z", "R", "T"]:
        obs = observed.select(component=component)
        syn = synthetic.select(component=component)
        if not obs or not syn:
            continue
        for obs_tr in obs:
        # in case there are multiple instruments
            config = copy.deepcopy(config_base)
            ws = pyflex.WindowSelector(obs_tr, syn, config, event=event,
                    station=stationxml)
            windows = ws.select_windows()
            print("Station %s.%s component %s picked %i windows" % (
                stationxml[0].code, stationxml[0][0].code, component,
                len(windows)))
            if not windows:
                continue
            all_windows.append(windows)
    return all_windows

a = time.time()
results = obsd_ds.process_two_files_without_parallel_output(synt_ds, window_func)
b = time.time()


if obsd_ds.mpi.rank == 0:
    print "WRITE OUT WINDOW..."
    for key, sta_win in results.iteritems():
        for comp_win in sta_win:
            print "comp_win", comp_win
            fn = comp_win[0].channel_id + ".win"
            fn = os.path.join(outputdir, fn)
            f = open(fn, 'w')
            f.write("%s\n" %comp_win[0].channel_id)
            f.write("%d\n" %len(comp_win))
            for win in comp_win:
                f.write("%10.2f %10.2f\n" % (win.relative_starttime, win.relative_endtime))
            f.close()
            print fn
    #print(results)
    print "Time taken:", b - a

del obsd_ds
del synt_ds
sys.exit()

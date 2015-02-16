import pyflex
from pyasdf import ASDFDataSet
import os
import glob
import time

eventname = "201302091416A"
obsd_fn = eventname + "_proc_27s_to_60s.h5"
synt_fn = eventname + "_proc_synt_27s_to_60s.h5"

if not os.path.exists(obsd_fn):
    raise ValueError("No obsd file: %s" %obsd_fn)
if not os.path.exists(synt_fn):
    raise ValueError("No synt file: %s" %synt_fn)

obsd_ds = ASDFDataSet(obsd_fn)
synt_ds = ASDFDataSet(synt_fn)

event = obsd_ds.events[0]

def weight_function(win):
    return win.max_cc_value

config = pyflex.Config(
    min_period=27.0, max_period=60.0,
    stalta_waterlevel=0.11,
    tshift_acceptance_level=15.0,
    dlna_acceptance_level=2.5,
    cc_acceptance_level=0.6,
    c_0=0.7, c_1=2.0, c_2=0.0, c_3a=1.0,
    c_3b=2.0, c_4a=3.0, c_4b=10.0,
    s2n_limit=0.5,
    max_time_before_first_arrival=-50.0,
    min_surface_wave_velocity=3.0,
    window_signal_to_noise_type="amplitude")

def window_func(this_station_group, other_station_group):
    # Make sure everything thats required is there.
    if not hasattr(this_station_group, "StationXML") or \
            not hasattr(this_station_group, "proc_27s_to_60s") or \
            not hasattr(other_station_group,
                        "proc_synt_27s_to_60s"):
        return

    stationxml = this_station_group.StationXML
    observed = this_station_group.proc_27s_to_60s
    synthetic = other_station_group.proc_synt_27s_to_60s

    all_windows = []

    for component in ["Z", "R", "T"]:
        obs = observed.select(component=component)
        syn = synthetic.select(component=component)
        if not obs or not syn:
            continue

        ws = pyflex.WindowSelector(obs, syn, config, event=event,
                station=stationxml)
        windows = ws.select_windows()
        print("Station %s.%s component %s picked %i windows" % (
            stationxml[0].code, stationxml[0][0].code, component,
            len(windows)))
        if not windows:
            continue
        all_windows.append(windows)
        #windows = pyflex.select_windows(
        #    obs, syn, config, event=event, station=stationxml)
        #print("Station %s.%s component %s picked %i windows" % (
        #    stationxml[0].code, stationxml[0][0].code, component,
        #    len(windows)))
        #if not windows:
        #    continue
        #all_windows.append(windows)
    return all_windows

a = time.time()
results = obsd_ds.process_two_files_without_parallel_output(synt_ds, window_func)
b = time.time()

if obsd_ds.mpi.rank == 0:
    print(results)
    print len(results)

print "Time taken:", b - a

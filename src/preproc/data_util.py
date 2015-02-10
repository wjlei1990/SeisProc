from obspy import read, read_inventory, readEvents
from obspy.core.util.geodetics import gps2DistAzimuth
import time
import glob
import os
import re

def find_first_digit(string):
    m = re.search("\d", string)
    return m.start()

def adjust_event_name(event_name):
    """
    Adjust from "C010104J" to "010104J"
    """
    pos=find_first_digit(event_name)
    return event_name[pos:]

def get_event_name(event):
    for i, desc in enumerate(event.event_descriptions):
        if desc.type == 'earthquake name':
            return desc.text

def process_data(filename, event = None, stationxml_dir = None, period_band = None, 
        npts=None, sampling_rate=None, output_dir=None):

    print "\nProcessing file: %s" %filename
    # interpolation value
    #npts = 3630
    #sampling_rate = 1.0  # Hz
    min_period = period_band[0]
    max_period = period_band[1]
    f2 = 1.0 / max_period
    f3 = 1.0 / min_period
    f1 = 0.8 * f2
    f4 = 1.2 * f3
    pre_filt = (f1, f2, f3, f4)

    # fetch event information
    event_name = get_event_name(event)
    short_event_name = adjust_event_name(event_name)

    output_path = output_dir
    print "output_path:", output_path
    if not os.path.exists(output_path):
        print "create dir"
        os.makedirs(output_path)

    origin = event.preferred_origin() or event.origins[0]
    event_latitude = origin.latitude
    event_longitude = origin.longitude
    event_time = origin.time
    event_depth = origin.depth
    starttime = event_time

    # read mseed file
    st = read(filename)
    print st
    nrecords = len(st)
    stname = st[0].stats.station
    nwname = st[0].stats.network

    # fetch station information and read stationxml file
    # print "LALALALA:",stationxml_dir, adjust_event_name
    stationxml_file = os.path.join(stationxml_dir, short_event_name, "%s.%s.xml" %(nwname, stname))
    print "Attaching stationxml file:", stationxml_file
    inv = read_inventory(stationxml_file)
    st.attach_response(inv)
    #st.plot()

    for i, tr in enumerate(st):
        #print tr.stats
        #tr.interpolate(sampling_rate=sampling_rate, starttime=starttime,
        #                npts=npts)
        #tr.decimate(4, strict_length=False,no_filter=True)
        print "Processing %d of total %d" %(i+1, nrecords)
        print "Detrend, Demean and Taper..."
        tr.detrend("linear")
        tr.detrend("demean")
        tr.taper(max_percentage=0.05, type="hann")
        #print "response show:"
        #print tr.stats.response
        print "Remove Response..."
        tr.remove_response(output="DISP", pre_filt=pre_filt, zero_mean=False,
                           taper=False)
        print "Detrend, Demean and Taper again..."
        tr.detrend("linear")
        tr.detrend("demean")
        tr.taper(max_percentage=0.05, type="hann")
        print "Interpolate..."
        try:
            tr.interpolate(sampling_rate=sampling_rate, starttime=starttime,
                           npts=npts)
        except Exception as e:
            print "error:", e
            return

    #rotate
    station_latitude = float(inv[0][0].latitude)
    station_longitude = float(inv[0][0].longitude)
    print type(station_latitude), type(station_longitude)
    print type(event_latitude), type(event_longitude)
    print station_latitude, station_longitude
    print event_latitude, event_longitude
    _, baz, _ = gps2DistAzimuth(station_latitude, station_longitude,
                                    event_latitude, event_longitude)

    print "here"
    components = [tr.stats.channel[-1] for tr in st]
    print "components:", components
    if "N" in components and "E" in components:
        print "Rotate"
        _, baz, _ = gps2DistAzimuth(station_latitude, station_longitude,
                                event_latitude, event_longitude)
        st.rotate(method="NE->RT", back_azimuth=baz)

    #output_fn = nwname + "." + stname + ".mseed"
    #output_path = os.path.join(output_dir, output_fn)
    #print output_path

    # save processed file
    #st.write(output_path, format="MSEED")
    for tr in st:
        comp = tr.stats.channel
        loc = tr.stats.location
        fn = stname + "." + nwname + "." + loc + ".BH" + comp[-1:] + ".sac"
        path = os.path.join(output_dir, fn)
        tr.write(path, format = "SAC")

    # save plot fig
    figure_name = nwname + "." + stname + ".png"
    figure_path = os.path.join(output_dir, figure_name)
    print "figure path:", figure_path
    st.plot(outfile=figure_path)

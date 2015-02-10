from obspy import read, read_inventory, readEvents
import time
import glob
import os
import re
import obspy
from obspy.core.util.geodetics import gps2DistAzimuth
from obspy.signal.invsim import c_sac_taper
import numpy as np

def find_first_digit(string):
    m = re.search("\d", string)
    return m.start()

def adjust_event_name(event_name):
    """
    Adjust from "C010104J" to "010104J"
    """
    pos=find_first_digit(event_name)
    return event_name[pos:]

def generate_station_list(datadir):
    matching_pattern = os.path.join(datadir, "*.MXE.sem.sac")
    filelist = glob.glob(matching_pattern)
    list1 = []
    for path in filelist:
        filename = path.split("/")[-1]
        info = filename.split(".")
        list1.append([info[0], info[1]])
    return list1

def get_event_name(event):
    for i, desc in enumerate(event.event_descriptions):
        if desc.type == 'earthquake name':
            return desc.text

def process_synt(datadir, station, event = None, stationxml_dir = None, period_band = None, npts=None,
                sampling_rate=None, output_dir=None, suffix=None):

    # ensemble the stream
    #station_list = generate_station_list(datadir)
    #for station in station_list:
    zdatafile = station[0] + "." + station[1] + ".MXZ.sem.sac"
    ndatafile = station[0] + "." + station[1] + ".MXN.sem.sac"
    edatafile = station[0] + "." + station[1] + ".MXE.sem.sac"
    zpath = os.path.join(datadir, zdatafile)
    npath = os.path.join(datadir, ndatafile)
    epath = os.path.join(datadir, edatafile)
    st = read(zpath)
    st2 = read(npath)
    st3 = read(epath)
    #print st
    #print st2
    st.append(st2[0])
    st.append(st3[0])

    #print "\nProcessing file: %s" %filename
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

    origin = event.preferred_origin() or event.origins[0]
    event_latitude = origin.latitude
    event_longitude = origin.longitude
    event_time = origin.time
    event_depth = origin.depth
    starttime = event_time
    print "event_time:",event_time

    #output_path = os.path.join(output_dir, short_event_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nrecords = len(st)
    # processing
    for i, tr in enumerate(st):
        #get component name
        cmpname = tr.stats.channel
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


        # Perform a frequency domain taper like during the response removal
        # just without an actual response...
        #for tr in st:
        print "Filtering..."
        data = tr.data.astype(np.float64)

        # smart calculation of nfft dodging large primes
        from obspy.signal.util import _npts2nfft
        nfft = _npts2nfft(len(data))

        fy = 1.0 / (tr.stats.delta * 2.0)
        freqs = np.linspace(0, fy, nfft // 2 + 1)

        # Transform data to Frequency domain
        data = np.fft.rfft(data, n=nfft)
        data *= c_sac_taper(freqs, flimit=pre_filt)
        data[-1] = abs(data[-1]) + 0.0j
        # transform data back into the time domain
        data = np.fft.irfft(data)[0:len(data)]
        # assign processed data and store processing information
        tr.data = data

        print "Detrend, Demean and Taper again..."
        tr.detrend("linear")
        tr.detrend("demean")
        tr.taper(max_percentage=0.05, type="hann")
        print "Interpolate..."
        try:
            tr.interpolate(sampling_rate=sampling_rate, starttime=starttime,
                           npts=npts)
        except:
            print "Error"
            return

    # rotate
    station_latitude = st[0].stats.sac['stla']
    station_longitude = st[0].stats.sac['stlo']
    event_latitude = st[0].stats.sac['evla']
    event_longitude = st[0].stats.sac['evlo']
    #print station_latitude, station_longitude
    #print station_latitude, station_longitude
    _, baz, _ = gps2DistAzimuth(station_latitude, station_longitude,
                                    event_latitude, event_longitude)
    print st
    st.rotate(method="NE->RT", back_azimuth=baz)
    # write out
    print st
    for tr in st:
        comp = tr.stats.channel
        outfn = station[0] + "." + station[1] + "." + comp + ".sac"
        if suffix is not None and suffix != "":
            outfn = outfn + "." + suffix
        outpath = os.path.join(output_dir, outfn)
        print "file saved:", outpath
        tr.stats.sac['b'] = 0
        tr.stats.sac['iztype'] = 9
        tr.write(outpath, format="SAC")
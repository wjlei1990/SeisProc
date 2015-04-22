import obspy
from obspy.core.util.geodetics import gps2DistAzimuth
from obspy.signal.invsim import c_sac_taper
import numpy as np
from pyasdf import ASDFDataSet
import glob
import os
import time

def process_synt(asdf_fn, outputfn, filter_band, old_tag=None, new_tag=None):
    # read in dataset
    ds = ASDFDataSet(asdf_fn)

    max_period = filter_band[1]
    min_period = filter_band[0]
    if min_period > max_period:
        raise ValueError("filter_band incorrect: min_period > max_period")
    f2 = 1.0 / max_period
    f3 = 1.0 / min_period
    f1 = 0.8 * f2
    f4 = 1.2 * f3
    pre_filt = (f1, f2, f3, f4)

    # read in event
    event = ds.events[0]
    origin = event.preferred_origin() or event.origins[0]
    event_latitude = origin.latitude
    event_longitude = origin.longitude
    event_time = origin.time

    # Figure out these parameters somehonw!
    starttime = event_time
    npts = 3600
    sampling_rate = 1.0

    def process_function(st, inv):
        st.detrend("linear")
        st.detrend("demean")
        st.taper(max_percentage=0.05, type="hann")

        # Perform a frequency domain taper like during the response removal
        # just without an actual response...
        for tr in st:
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

        st.detrend("linear")
        st.detrend("demean")
        st.taper(max_percentage=0.05, type="hann")

        st.interpolate(sampling_rate=sampling_rate, starttime=starttime,
                    npts=npts)

        components = [tr.stats.channel[-1] for tr in st]
        if "N" in components and "E" in components:
            station_latitude = float(inv[0][0].latitude)
            station_longitude = float(inv[0][0].longitude)
            _, baz, _ = gps2DistAzimuth(station_latitude, station_longitude,
                                    event_latitude, event_longitude)

            st.rotate(method="NE->RT", back_azimuth=baz)

        # Convert to single precision to save space.
        for tr in st:
            tr.data = np.require(tr.data, dtype="float32")

        return st

    tag_map = {
            old_tag : new_tag
    }
    
    # process
    ds.process(process_function, outputfn, tag_map=tag_map)

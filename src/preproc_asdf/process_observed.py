import obspy
from obspy.core.util.geodetics import gps2DistAzimuth
import numpy as np
import os
import glob
import time
from pyasdf import ASDFDataSet

t1 = time.time()

eventname = "010403A"
old_tag = "raw_observed"

basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/raw"
outputdir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/proc"

asdf_fn = eventname + "." + old_tag + ".h5"
asdf_fn = os.path.join(basedir, asdf_fn)

if not os.path.exists(asdf_fn):
    raise ValueError("No asdf file found: %s" %asdf_fn)
print "Input file:", asdf_fn

# read in dataset
ds = ASDFDataSet(asdf_fn)

# read in event
event = ds.events[0]
origin = event.preferred_origin() or event.origins[0]
event_latitude = origin.latitude
event_longitude = origin.longitude
event_time = origin.time

# Figure out interpolation parameters 
starttime = event_time
npts = 3600
sampling_rate = 1.0

# Loop over both period sets. This will result in two files. It could also be
# saved to the same file.
for min_period, max_period in [(35.0, 60.0), (60, 120)]:
#for min_period, max_period in [(35.0, 60.0)]:
    f2 = 1.0 / max_period
    f3 = 1.0 / min_period
    f1 = 0.8 * f2
    f4 = 1.2 * f3
    pre_filt = (f1, f2, f3, f4)

    def process_function(st, inv):
        st.detrend("linear")
        st.detrend("demean")
        st.taper(max_percentage=0.05, type="hann")

        st.attach_response(inv)
        st.remove_response(output="DISP", pre_filt=pre_filt, zero_mean=False,
                           taper=False)

        st.detrend("linear")
        st.detrend("demean")
        st.taper(max_percentage=0.05, type="hann")

        st.interpolate(sampling_rate=sampling_rate, starttime=starttime,
                       npts=npts)

        station_latitude = float(inv[0][0].latitude)
        station_longitude = float(inv[0][0].longitude)
        _, baz, _ = gps2DistAzimuth(station_latitude, station_longitude,
                                    event_latitude, event_longitude)

        components = [tr.stats.channel[-1] for tr in st]
        if "N" in components and "E" in components:
            st.rotate(method="NE->RT", back_azimuth=baz)

        # Convert to single precision to save space.
        for tr in st:
            tr.data = np.require(tr.data, dtype="float32")

        return st

    new_tag = "proc_obsd_%i_%i" % (int(min_period), int(max_period))

    tag_map = {
        old_tag : new_tag 
    }

    outputfn = eventname + "." + new_tag + ".h5"
    outputfn = os.path.join(outputdir, outputfn)
    if os.path.exists(outputfn):
        os.remove(outputfn)
    ds.process(process_function, outputfn, tag_map=tag_map)

t2=time.time()

print "Elapsed time:", t2-t1

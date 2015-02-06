import glob
import os

from pyasdf import ASDFDataSet

filename = "synthetic.h5"

def convert_asdf(filelist, asdf_fn, staxml_filelist=None, quakemlfile=None, tag=None):

    nfiles = len(filelist)
    if nfiles == 0:
        print "No file specified. Return..."
        return

    if os.path.exists(asdf_fn):
        raise Exception("File '%s' exists." % filename)

    ds = ASDFDataSet(asdf_fn)

    # Add event
    if quakemlfile is not None and os.path.exists(quakemlfile):
        print "Event info added"
        ds.add_quakeml(quakemlfile)
        event = ds.events[0]
    else:
        print "No event info added"
        event = None

    # Add waveforms.
    print "Adding Waveform data"
    for _i, filename in enumerate(filelist):
        if os.path.exists(filename):
            #print("Adding file %i of %i: %s" % (_i + 1, 
            #       len(filelist), os.path.basename(filename)))
            #ds.add_waveforms(filename, tag="synthetic", event_id=event)
            ds.add_waveforms(filename, tag=tag)
        else:
            print("File not exist %i of %i")

    # Add StationXML files.
    if staxml_filelist is not None and len(staxml_filelist) > 0: 
        #search_pattern = os.path.join(stationxml_dir, "*.xml")
        #filenames = glob.glob(search_pattern)
        for _i, filename in enumerate(staxml_filelist):
            if os.path.exists(filename):
                print("Adding StationXML file %i of %i..." % (_i + 1, len(filenames)))
                ds.add_stationxml(filename)
    else:
        print("No stationxml added")

import glob
import os
from pyasdf import ASDFDataSet

def convert_asdf(filelist, asdf_fn, quakemlfile, staxml_filelist=None, tag=None):

    nfiles = len(filelist)
    if nfiles == 0:
        print "No file specified. Return..."
        return

    if os.path.exists(asdf_fn):
        raise Exception("File '%s' exists." % asdf_fn)

    ds = ASDFDataSet(asdf_fn)

    # Add event
    if quakemlfile is not None and os.path.exists(quakemlfile):
        print "Event info added"
        ds.add_quakeml(quakemlfile)
        event = ds.events[0]
    else:
        raise ValueError("No Event file")

    # Add waveforms.
    print "Adding Waveform data"
    for _i, filename in enumerate(filelist):
        if os.path.exists(filename):
            #print("Adding file %i of %i: %s" % (_i + 1, 
            #       len(filelist), os.path.basename(filename)))
            ds.add_waveforms(filename, tag=tag, event_id=event)
        else:
            print("File not exist %i of %i")

    # Add StationXML files.
    if staxml_filelist is not None and len(staxml_filelist) > 0: 
        for _i, filename in enumerate(staxml_filelist):
            if os.path.exists(filename):
                #print("Adding StationXML file %i of %i..." % (_i + 1, len(filenames)))
                ds.add_stationxml(filename)
    else:
        print("No stationxml added")

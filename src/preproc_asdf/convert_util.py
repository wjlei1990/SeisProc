import glob
import os

from pyasdf import ASDFDataSet

filename = "synthetic.h5"

def convert_to_synt_asdf(filelist, asdf_fn, stationxml_dir=None, quakemlfile=None):

    nfiles = len(filelist)
    if nfiles == 0:
        print "No file specified. Return..."
        return

    if os.path.exists(asdf_fn):
        #raise Exception("File '%s' exists." % filename)
        os.remove(asdf_fn)

    ds = ASDFDataSet(asdf_fn)

    # Add event
    if quakemlfile is not None and os.path.exists(quakemlfile):
        ds.add_quakeml(quakemlfile)
        event = ds.events[0]
    else:
        event = None

    # Add waveforms.
    for _i, filename in enumerate(filelist):
        if os.path.exists(filename):
            print("Adding SAC file %i of %i..." % (_i + 1, len(filenames)))
            #ds.add_waveforms(filename, tag="synthetic", event_id=event)
            ds.add_waveforms(filename, tag="synthetic")
        else:
            print("File not exist %i of %i")

    # Add StationXML files.
    if stationxml_dir is not None and os.path.exists(stationxml_dir): 
        search_pattern = os.path.join(stationxml_dir, "*.xml")
        filenames = glob.glob(search_pattern)
        for _i, filename in enumerate(filenames):
            print("Adding StationXML file %i of %i..." % (_i + 1, len(filenames)))
            ds.add_stationxml(filename)

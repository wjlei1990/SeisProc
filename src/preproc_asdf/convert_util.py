import glob
import os
from pyasdf import ASDFDataSet

def convert_to_asdf(filelist, asdf_fn, quakemlfile, staxml_filelist=None, tag=None):
    """
    Convert files(sac or mseed) to asdf
    """

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


def convert_to_sac(asdf_fn, outputdir, tag=None, type="sac"):
    """
    Convert asdf to different types of file
    """
    if not os.path.exists(asdf_fn):
        raise ValueError("No asdf file: %s" % asdf_fn)

    if not os.path.exists(outputdir):
        raise ValueError("No output dir: %s" % outputdir)

    ds = ASDFDataSet(asdf_fn)

    sta_list = ds.get_station_list()
    print sta_list
    print "tag",tag

    for sta_tag in sta_list:
        station_name = sta_tag.replace(".", "_")
        station = getattr(ds.waveforms, station_name)
        attr_list = dir(station)
        attr_list.remove('StationXML')
        print station_name, attr_list
        if tag is None or tag == "":
            if len(attr_list) == 1:
                stream = getattr(station, attr_list[0])
        else:
            stream = getattr(station, tag)
        #print sta_tag, stream
        for tr in stream:
            network = tr.stats.network
            station = tr.stats.station
            location = tr.stats.location
            channel = tr.stats.channel
            filename = ".".join([network, station, location, channel, type])
            filename = os.path.join(outputdir, filename)
            print "output filename:", filename
            tr.write(filename, format=type)




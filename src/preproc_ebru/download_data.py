import obspy
from obspy.fdsn import Client
import os
import warnings
import datetime

def data_download(stations, starttime, endtime, event_name):

    print "\n========================================"
    print "event:", event_name
    print "time:", starttime, endtime
    waveforms_folder = "waveforms/" + event_name
    stationxml_folder = "stationxml/" + event_name
    c = Client("IRIS")

    if not os.path.exists(waveforms_folder):
        os.makedirs(waveforms_folder)

    if not os.path.exists(stationxml_folder):
        os.makedirs(stationxml_folder)

    for network, station in stations:
        ### First download waveforms.
        filename = os.path.join(waveforms_folder,
                            "%s.%s.mseed" % (network, station))
        if os.path.exists(filename):
            continue

        try:
            c.get_waveforms(network=network, station=station, location="*",
                            channel="BH?", starttime=starttime, endtime=endtime,
                            filename=filename)
        except Exception as e:
            print("Failed to download %s.%s due to %s" %
                (network, station, str(e)))
            continue

        print("Successfully downloaded %s." % filename)
        ###

        ### Then download stationxml file
        stationxml_filename = os.path.join(stationxml_folder,
                                       "%s.%s.xml" % (network, station))

        if os.path.exists(stationxml_filename):
            continue

        try:
            c.get_stations(network=network, station=station, location="*",
                            channel="BH?", starttime=starttime, endtime=endtime,
                            filename=stationxml_filename, level="response")
        except Exception as e:
            print("Failed to download %s.%s StationXML due to %s" % (
                network, station, str(e)))
            continue

        print("Successfully downloaded %s." % stationxml_filename)
        ###

def read_station_file(station_filename):
    stations = []
    with open(station_filename, "rt") as fh:
        for line in fh:
            line = line.split()
            stations.append((line[1], line[0]))
    return stations


def read_cmt_file(filename):
    """
    Initialize a source object from a CMTSOLUTION file.
    :param filename: path to the CMTSOLUTION file
    """
    with open(filename, "rt") as f:
        line = f.readline()
        origin_time = line[4:].strip().split()[:6]
        values = list(map(int, origin_time[:-1])) + [ float(origin_time[-1]) ]
        try:
            origin_time = obspy.UTCDateTime(*values)
            print origin_time
        except (TypeError, ValueError):
            warnings.warn("Could not determine origin time from line: %s" % line)
            origin_time = obspy.UTCDateTime(0)
        event_name = f.readline().split()[-1]
        # print type(data), data
        #event_name = float(f.readline().strip().split()[-1])
        time_shift = float(f.readline().strip().split()[-1])
        half_duration = float(f.readline().strip().split()[-1])
        latitude = float(f.readline().strip().split()[-1])
        longitude = float(f.readline().strip().split()[-1])
        depth_in_m = float(f.readline().strip().split()[-1]) * 1e3
        m_rr = float(f.readline().strip().split()[-1]) / 1e7
        m_tt = float(f.readline().strip().split()[-1]) / 1e7
        m_pp = float(f.readline().strip().split()[-1]) / 1e7
        m_rt = float(f.readline().strip().split()[-1]) / 1e7
        m_rp = float(f.readline().strip().split()[-1]) / 1e7
        m_tp = float(f.readline().strip().split()[-1]) / 1e7
    return (latitude, longitude, depth_in_m, m_rr, m_tt, m_pp, m_rt,
            m_rp, m_tp, time_shift, origin_time, event_name, half_duration)


def read_cmt_list(cmt_list_file):
    cmt_list = []
    with open(cmt_list_file) as f:
        content = f.read().splitlines()
        #print "content:", content
        #cmt_list.append(content)
    return content

station_filename = "./STATIONS"
station_list = read_station_file(station_filename)
print "station_list:", station_list

cmt_dir = "./cmt"
cmt_list_file = "./cmt_list"
cmt_list = read_cmt_list(cmt_list_file)
print "cmt_info:", cmt_list

for cmt in cmt_list:
    cmt_file = os.path.join(cmt_dir, cmt)
    cmt_info = read_cmt_file(cmt_file)
    event_name = cmt_info[11]
    calibrate_time = cmt_info[10] + datetime.timedelta(seconds=int(cmt_info[9]))
    starttime = calibrate_time + datetime.timedelta(seconds=-300)
    endtime = calibrate_time + datetime.timedelta(seconds=3600)
    data_download(station_list, starttime, endtime, event_name)

#print cmt_info
#print starttime, endtime

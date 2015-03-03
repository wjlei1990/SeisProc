import obspy
from os import listdir
from os.path import isfile, join
from obspy.core import read
import matplotlib.pyplot as plt
from download_data import read_cmt_file
from obspy.core.util.geodetics.base import gps2DistAzimuth

import numpy as np
from mpl_toolkits.basemap import Basemap
from obspy.imaging.beachball import Beach
from pylab import *

import sys
import os

#close all the plots
plt.close('all')

def read_station(station_file):
    station_info = {}
    with open(station_file, 'r') as fh:
        for line in fh:
            line = line.split()
            #print line
            [station, nw, lat, lon, elevation, burial] = line
            #print station, nw, lat,lon, elevation, burial
            key = nw + '.' + station
            station_info[key] = [station, nw, float(lat), float(lon), float(elevation), float(burial)]
    return station_info

def sort_azimuth(theta, n):
    num=[ 0 for i in range(n)]
    delta = 2*np.pi/n;
    index = [ i for i in range(n)]
    bins = [ delta*value for value in index ]
    bins_temp = [ delta*i for i in range(n+1) ]
    for i in range(n):
        count=0
        for j in theta:
            if j>=bins_temp[i] and j<bins_temp[i+1]:
                count += 1
        num[i] = count
    return bins, num

if len(sys.argv) != 2:
    raise ValueError('Input Argument Wrong!')
else:
    event=sys.argv[1]

basedir='./waveforms'
outputdir='./output'
eventpath = join(basedir, event)
onlyfiles = [ f for f in listdir(eventpath) if isfile(join(eventpath,f)) ]

# get station information
station_file = './STATIONS'
station = read_station(station_file)
#print station
lats=[]
lons=[]
for datafile in onlyfiles:
    path = join(eventpath, datafile)
    #print path
    st=read(path)
    tr=st[0]
    key = tr.stats.network + '.' + tr.stats.station
    station_info = station[key]
    lon = station_info[3]
    lat = station_info[2]
    #print "***"
    #print "lon,lat:", lon, lat, type(lon),type(lat)
    if lon < 0:
        lon += 360
    #print "lon,lat:", lon, lat, type(lon),type(lat)
    lats.append(lat)
    lons.append(lon)

# read cmt_info
cmt_file = './cmt/' + event
cmt_info = read_cmt_file(cmt_file)
cmt_lat = cmt_info[0]
cmt_lon = cmt_info[1]
cmt_depth = cmt_info[2]
moment_tensor = cmt_info[3:9]
event_name = cmt_info[-2]

###
### plot first figure
###
ax = plt.subplot(211)
plt.title(event_name)
m = Basemap(projection='cyl', lon_0=142.36929, lat_0=38.3215,
            resolution='c')

m.drawcoastlines()
m.fillcontinents()
m.drawparallels(np.arange(-90., 120., 30.))
m.drawmeridians(np.arange(0., 420., 60.))
m.drawmapboundary()

x, y = m(lons, lats)
m.scatter(x, y, 30, color="r", marker="^", edgecolor="k", linewidth='0.3', zorder=3)

focmecs = [moment_tensor,]
ax = plt.gca()
for i in range(len(focmecs)):
    b = Beach(focmecs[i], xy=(cmt_lon, cmt_lat), width=10, linewidth=1)
    b.set_zorder(10)
    ax.add_collection(b)

earth_hc, _ , _ = gps2DistAzimuth(0,0,0, 180)
##plot azimuth and distance distribution
theta=[]
radius=[]
for i in range(len(lons)):
    geo_info = gps2DistAzimuth(cmt_lat, cmt_lon, lats[i], lons[i])
    #geo_info = gps2DistAzimuth(lats[i], lons[i], cmt_loc[0], cmt_loc[1])
    #print geo_info
    theta.append(geo_info[1]/180.0*np.pi)
    radius.append(geo_info[0]/earth_hc)



ax = plt.subplot(223, polar=True)
c = plt.scatter(theta, radius, marker=u'^', c='r', s=10, edgecolor='k', linewidth='0.3')
c.set_alpha(0.75)
plt.xticks(fontsize=8)
plt.yticks(fontsize=6)


#print theta

bins, num = sort_azimuth(theta, 16)
print "bins:",bins
print "nums:", num

#ax = pl.axes([0.025, 0.025, 0.95, 0.95], polar=True)

ax = plt.subplot(224, polar=True)
#N = 20
#theta = np.arange(0.0, 2 * np.pi, 2 * np.pi / N)
#radii = 10 * np.random.rand(N)
#width = np.pi / 4 * np.random.rand(N)
bars = plt.bar(bins, num, width=(bins[1]-bins[0]), bottom=0.0)

for r, bar in zip(num, bars):
    bar.set_facecolor(plt.cm.jet(r/16.))
    bar.set_alpha(0.5)
    bar.set_linewidth(0.3)

#ax.set_xticklabels([])
#ax.set_yticklabels([])
plt.xticks(fontsize=8)
plt.yticks(fontsize=6)
#for tick in ax.yaxis.get_major_ticks():
#    tick.label.set_fontsize(5)

outputfn = os.path.join(outputdir, '%s.pdf' %event )
if not os.path.exists(outputdir):
    os.makedirs(outputdir)
#pl.show()
savefig(outputfn,dpi = 300)
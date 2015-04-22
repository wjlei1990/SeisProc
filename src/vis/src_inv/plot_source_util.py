from obspy.imaging.beachball import Beach
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from source import Source
import matplotlib.gridspec as gridspec
import os
import glob
import sys
import re

def plot_si_bb(ax, cmt):
    # get moment tensor
    mt = [ float(cmt.m_rr), cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
    print "inside:", mt
    print mt[0]
    print type(mt[0])
    # plot beach ball
    b = Beach(mt, linewidth=1, xy=(0, 0.6), width=1.5, size=2, facecolor='r')
    ax.add_collection(b)
    # set axis
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1.5])
    ax.set_aspect('equal')
    # magnitude
    text = "Mw=%4.3f" %cmt.moment_magnitude
    plt.text(-0.9, -0.3, text, fontsize=7)
    # lat and lon
    text = "lat=%6.3f$^\circ$; lon=%6.3f$^\circ$" %(cmt.latitude, cmt.longitude)
    plt.text(-0.9, -0.5, text, fontsize=7)
    #depth
    text = "dep=%6.3f km;" %(cmt.depth_in_m/1000.0)
    plt.text(-0.9, -0.7, text, fontsize=7)
    ax.set_xticks([])
    ax.set_yticks([])
    # title
    text = "Init CMT"
    plt.text(-0.9, 1.3, text, fontsize=7)
    
def plot_si_bb_comp(ax, cmt, cmt_init, tag, runfile):
    # get moment tensor
    mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
    # plot beach ball
    b = Beach(mt, linewidth=1, xy=(0, 0.6), width=1.5, size=2, facecolor='r')
    ax.add_collection(b)
    # set axis
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1.5])
    ax.set_aspect('equal')
    # magnitude energy change
    dmag = cmt.moment_magnitude - cmt_init.moment_magnitude
    deltam = (cmt.M0 - cmt_init.M0) / cmt_init.M0
    print "delta energy:", deltam, dmag
    text = r"$\Delta$M=%4.3f(%4.3f%%)" %(dmag, deltam * 100.0)
    plt.text(-0.9, -0.3, text, fontsize=7)
    # lat and lon
    text = r"$\Delta$lat=%6.3f$^\circ$; $\Delta$lon=%6.3f$^\circ$" %(cmt.latitude-cmt_init.latitude, cmt.longitude-cmt_init.longitude)
    plt.text(-0.9, -0.5, text, fontsize=7)
    # depth
    text = r"$\Delta$dep=%6.3f km;" %((cmt.depth_in_m-cmt_init.depth_in_m)/1000.0)
    plt.text(-0.9, -0.7, text, fontsize=7)
    ax.set_xticks([])
    ax.set_yticks([])
    # variance reduction
    if os.path.exists(runfile):
        red_val = get_variance_reduction(runfile)
        text = r"$\Delta$Var=%4.3f%%" %(red_val)
        plt.text(-0.9, -0.9, text, fontsize=7)

    text = tag
    plt.text(-0.9, 1.3, text, fontsize=7)

def get_variance_reduction(filename):
    
    fh = open(filename, 'r')
    for line in fh:
        if re.search("Total Variance reduced from", line):
            ma = re.search("Total Variance reduced from(\s+)(\S+)(\s+)to(\s+)(\S+)(\s+)=(\s+)(\S+)", line)
            red_value = float(ma.group(8))
    return red_value

def plot_si_result(basedir, event_name, outputdir, type_tag):

    cmtbase = os.path.join(basedir, "CMTSOLUTION_%s" %event_name)
    runfilebase = os.path.join(basedir, "xcmt3d_%s" %event_name)
    print "Plotting event:", event_name
    print "Base:", cmtbase

    fig1 = plt.figure(num=2, figsize=(7, 10), dpi=80, facecolor='w', edgecolor='k')
    G = gridspec.GridSpec(3, 3)

    loc_mapping = {'6p_ZT':G[0,0], '7p_ZT':G[0,1], '9p_ZT':G[0,2],
                '6p_ZT_DC':G[1,0], '7p_ZT_DC':G[1,1], '9p_ZT_DC':G[1,2]}

    # Original CMT
    ax = plt.subplot(G[2,2])
    cmtfile = cmtbase + "_init"
    print "cmtfile:", cmtfile
    cmt_init = Source.from_CMTSOLUTION_file(cmtfile)
    mt_init = [cmt_init.m_rr, cmt_init.m_tt, cmt_init.m_pp, cmt_init.m_rt, cmt_init.m_rp, cmt_init.m_tp]
    print mt_init
    #print cmt_init.moment_magnitude
    #plot_si_bb(ax, cmt_init)

    # Source Inversion result
    for tag, position in loc_mapping.iteritems():
        ax = plt.subplot(position)
        cmtfile = cmtbase + "_" + tag
        print "cmtfile:", cmtfile
        runfile = runfilebase + "_" + tag + ".out"
        cmt = Source.from_CMTSOLUTION_file(cmtfile)
        #print cmt.moment_magnitude
        mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
        plot_si_bb_comp(ax, cmt, cmt_init, tag, runfile)

    # Map and source location
    ax = plt.subplot(G[2,:-1])
    m = Basemap(projection='cyl', lon_0=142.36929, lat_0=0.0, resolution='c')
    m.drawcoastlines()
    m.fillcontinents()
    m.drawparallels(np.arange(-90., 120., 30.))
    m.drawmeridians(np.arange(0., 420., 60.))
    m.drawmapboundary()
    # Beachball on the map
    #calibrate longitude
    if cmt.longitude < 0:
        lon = cmt.longitude + 360
    else:
        lon = cmt.longitude
    x, y = m(lon, cmt.latitude)
    #print cmt.longitude, cmt.latitude
    #print x, y
    #b = Beach(mt_init, xy=(x,y), width=20, linewidth=1, alpha=0.85)
    #b.set_zorder(100)
    #ax.add_collection(b)
    fig_title = "%s_%s" %(event_name, type_tag)
    plt.title(fig_title)

    outputfile = "%s_%s.pdf" %(event_name, type_tag)
    path = os.path.join(outputdir, outputfile)
    print "Output file:", path

    fig1.savefig(path)

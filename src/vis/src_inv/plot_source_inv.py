from obspy.imaging.beachball import Beach
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from source import Source
import matplotlib.gridspec as gridspec

def plot_si_bb(ax, cmt):
    # get moment tensor
    mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
    # plot beach ball
    b = Beach(mt, linewidth=1, xy=(0, 0.6), width=1.5, size=2, facecolor='r')
    ax.add_collection(b)
    # set axis
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1.5])
    ax.set_aspect('equal')
    # magnitude
    text = "Mw=%3.2f" %cmt.moment_magnitude
    plt.text(-0.9, -0.3, text, fontsize=7)
    # lat and lon
    text = "lat=%6.2f$^\circ$; lon=%6.2f$^\circ$" %(cmt.latitude, cmt.longitude)
    plt.text(-0.9, -0.5, text, fontsize=7)
    #depth
    text = "dep=%6.2f km;" %(cmt.depth_in_m/1000.0)
    plt.text(-0.9, -0.7, text, fontsize=7)
    #ax.set_xticks([])
    #ax.set_yticks([])
    # title
    text = "Init CMT"
    plt.text(-0.9, 1.3, text, fontsize=7)
    
def plot_si_bb_comp(ax, cmt, cmt_init):
    # get moment tensor
    mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
    # plot beach ball
    b = Beach(mt, linewidth=1, xy=(0, 0.6), width=1.5, size=2, facecolor='r')
    ax.add_collection(b)
    # set axis
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1.5])
    ax.set_aspect('equal')
    # magnitude
    text = r"$\Delta$Mw=%3.2f" %(cmt.moment_magnitude-cmt_init.moment_magnitude)
    plt.text(-0.9, -0.3, text, fontsize=7)
    # lat and lon
    text = r"$\Delta$lat=%6.2f$^\circ$; $\Delta$lon=%6.2f$^\circ$" %(cmt.latitude-cmt_init.latitude, cmt.longitude-cmt_init.longitude)
    plt.text(-0.9, -0.5, text, fontsize=7)
    #depth
    text = r"$\Delta$dep=%6.2f km;" %((cmt.depth_in_m-cmt_init.depth_in_m)/1000.0)
    plt.text(-0.9, -0.7, text, fontsize=7)
    ax.set_xticks([])
    ax.set_yticks([])
    
event_name = "010104J"

fig1 = plt.figure(num=2, figsize=(7, 10), dpi=80, facecolor='w', edgecolor='k')
G = gridspec.GridSpec(3, 3)

# Original CMT
ax = plt.subplot(G[2,2])
cmtfile = "./cmt/" + event_name + "_init"
cmt_init = Source.from_CMTSOLUTION_file(cmtfile)
mt_init = [cmt_init.m_rr, cmt_init.m_tt, cmt_init.m_pp, cmt_init.m_rt, cmt_init.m_rp, cmt_init.m_tp]
print cmt_init.moment_magnitude
plot_si_bb(ax, cmt_init)

# 6ZT
ax = plt.subplot(G[0,0])
cmtfile = "./cmt/" + event_name + "_6p_ZT"
cmt = Source.from_CMTSOLUTION_file(cmtfile)
print cmt.moment_magnitude
mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
plot_si_bb_comp(ax, cmt, cmt_init)

# 7ZT
ax = plt.subplot(G[0,1])
cmtfile = "./cmt/" + event_name + "_7p_ZT"
cmt = Source.from_CMTSOLUTION_file(cmtfile)
print cmt.moment_magnitude
mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
plot_si_bb_comp(ax, cmt, cmt_init)

# 9ZT
ax = plt.subplot(G[0,2])
cmtfile = "./cmt/" + event_name + "_9p_ZT"
cmt = Source.from_CMTSOLUTION_file(cmtfile)
print cmt.moment_magnitude
mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
plot_si_bb_comp(ax, cmt, cmt_init)

# 6ZT+DC
ax = plt.subplot(G[1,0])
cmtfile = "./cmt/" + event_name + "_6p_ZT_DC"
cmt = Source.from_CMTSOLUTION_file(cmtfile)
print cmt.moment_magnitude
mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
plot_si_bb_comp(ax, cmt, cmt_init)

# 7ZT+DC
ax = plt.subplot(G[1,1])
cmtfile = "./cmt/" + event_name + "_7p_ZT_DC"
cmt = Source.from_CMTSOLUTION_file(cmtfile)
print cmt.moment_magnitude
mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
plot_si_bb_comp(ax, cmt, cmt_init)

# 9ZT+DC
ax = plt.subplot(G[1,2])
cmtfile = "./cmt/" + event_name + "_9p_ZT_DC"
cmt = Source.from_CMTSOLUTION_file(cmtfile)
print cmt.moment_magnitude
mt = [cmt.m_rr, cmt.m_tt, cmt.m_pp, cmt.m_rt, cmt.m_rp, cmt.m_tp]
plot_si_bb_comp(ax, cmt, cmt_init)

# Map
ax = plt.subplot(G[2,:-1])
m = Basemap(projection='cyl', lon_0=142.36929, lat_0=0.0, resolution='c')
m.drawcoastlines()
m.fillcontinents()
m.drawparallels(np.arange(-90., 120., 30.))
m.drawmeridians(np.arange(0., 420., 60.))
m.drawmapboundary()
# Beachball on the map
x, y = m(cmt.longitude, cmt.latitude)
#print cmt.longitude, cmt.latitude
#print x, y
b = Beach(mt_init, xy=(x,y), width=20, linewidth=1, alpha=0.85)
#b.set_zorder(100)
ax.add_collection(b)

fig1.savefig("test.png")
plt.show()

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


event_info = np.loadtxt("event.log")

plt.figure(figsize=(20,10), dpi=100)
m = Basemap(projection='cyl', lon_0=0.0, lat_0=0.0,
            resolution='c')
m.drawcoastlines()
m.fillcontinents()
m.drawparallels(np.arange(-90., 120., 30.))
m.drawmeridians(np.arange(0., 420., 60.))
m.drawmapboundary()

x, y = m(event_info[:,1], event_info[:,0])
m.scatter(x, y, 60, color="r", marker="o", edgecolor="k", linewidth='0.3', zorder=3)

plt.title("Earthquake location map")

plt.savefig("deep_event_location.png")



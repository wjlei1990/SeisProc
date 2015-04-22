import obspy
import numpy as np
import glob
import os
import time
from process_synthetic_util import process_synt

eventname = "010403A"
old_tag = "raw_synthetic"

basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/raw"
outputdir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/proc"

type_list = ["", "Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp", "dep", "lon", "lat"]
#type_list = ["Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp", "dep", "lon", "lat"]
#type_list = ["", ]

filter_band_list = [[35, 60], [60, 120]]

for type in type_list:
    print "=============================="
    print "type:", type
    if type == "":
        asdf_fn = eventname + "." + old_tag + ".h5"
    else:
        asdf_fn = eventname + "." + type  + "." + old_tag + ".h5"
    asdf_fn = os.path.join(basedir, asdf_fn)
    if not os.path.exists(asdf_fn):
        raise ValueError("No asdf file found %s" %asdf_fn)
    print "input asdf:", asdf_fn
    for filter_band in filter_band_list:
        t1 = time.time()
        print "=========="
        new_tag = "proc_synt_%i_%i" % (int(filter_band[0]), int(filter_band[1]))
        if type == "":
            outputfn = eventname + "." + new_tag + ".h5"
        else:
            outputfn = eventname + "." + type + "." + new_tag + ".h5"
        outputfn = os.path.join(outputdir, outputfn)

        print "tag: %s  %s" % (old_tag, new_tag)
        print "filter band:", filter_band
        print "Output:", outputfn 
    
        process_synt(asdf_fn, outputfn, filter_band, old_tag=old_tag, new_tag=new_tag)
        t2 = time.time()
        print "Elapsed time:", t2-t1

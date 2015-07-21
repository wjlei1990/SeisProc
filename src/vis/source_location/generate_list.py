import os
import glob
from source import *

#cmtdir = "/ccs/home/lei/SOURCE_INVERSION/combine_together/cmt"
cmtdir = "/ccs/home/lei/SeisProc/src/vis/src_inv_pool/deep"
filelist = glob.glob(os.path.join(cmtdir,"*"))

f = open('event.log', 'w')

for cmtfile in filelist:
    cmt = CMTSource.from_CMTSOLUTION_file(cmtfile)
    f.write("%8.2f %8.2f %8.2f\n" %(cmt.latitude, cmt.longitude, cmt.depth_in_m/1000.))

f.close()

print "Number of cmt files:", len(filelist)

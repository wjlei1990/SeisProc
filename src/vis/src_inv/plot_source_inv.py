import os
import glob
import sys
from plot_source_util import *

if len(sys.argv) != 3:
    raise ValueError("Incorrect arg number")

event_name = sys.argv[1]
type_tag = sys.argv[2]

basedir = "/ccs/home/lei/SeisProc/src/cmt3d/XFILES_RESULT"
basedir = basedir + "_" + type_tag

outputdir="result"

if not os.path.exists(outputdir):
    os.mkdir(outputdir)

plot_si_result(basedir, event_name, outputdir, type_tag)

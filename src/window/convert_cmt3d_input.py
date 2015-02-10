import os
import glob

basedir = "/home/lei/Research/SOURCE_INVERSION/DATA"
eventname = "010104J_27_60"

outputbase = "/home/lei/Research/SOURCE_INVERSION/DATA/window/CMT3D_INPUT"
outputfile = os.path.join(outputbase, eventname)

windir = os.path.join(basedir, "window", eventname)
alllist = glob.glob( windir + "/*.win")

print len(alllist)

n_used = 0
n_unused = 0

fo = open(outputfile, "w")
filelist = []

for winfile in alllist:
    basename = os.path.basename(winfile)
    sta_info = basename.split(".")
    sta = sta_info[0]
    nw = sta_info[1]
    loc = sta_info[2]
    comp = sta_info[3]
    #print "%s:%s %s %s %s" %(basename, sta, nw, loc, comp)
    if loc == "" or loc == "00":
        n_used += 1
        filelist.append(winfile)
    else:
        print "%s:%s %s %s %s" %(basename, sta, nw, loc, comp)
        n_unused += 1

print "Total number of winfile used:", len(filelist)
fo.write("%d\n" %n_used)

for winfile in filelist:
    basename = os.path.basename(winfile)
    sta_info = basename.split(".")
    sta = sta_info[0]
    nw = sta_info[1]
    loc = sta_info[2]
    comp = sta_info[3]
    obsd_fn = "%s.%s.%s.BH%s.sac" %(sta, nw, loc, comp[-1:])
    synt_fn = "%s.%s.MX%s.sac" %(sta, nw, comp[-1:])
    obsd_fn = os.path.join(basedir, "OBSD_PROC", eventname, obsd_fn)
    synt_fn = os.path.join(basedir, "SYNT_PROC", eventname, synt_fn)
    fwin = open(winfile, "r")
    content = fwin.readlines()
    content_write = content[1:]
    #print content_write
    fo.write("%s\n" %obsd_fn)
    fo.write("%s\n" %synt_fn)
    for line in content_write:
        fo.write(line)

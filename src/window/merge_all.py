# merge win files for different frequency band
import os
import glob
import sys

def merge_windfile(winfiledir, event):

    outputfile = os.path.join(winfiledir, "%s.cmt_input" %event)

    search_pattern = os.path.join(winfiledir, "*%s*" %event)
    filelist = glob.glob(search_pattern)
    for fn in filelist:
        if ".cmt_input" in fn:
            filelist.remove(fn)

    #print search_pattern
    print "Merging files:",filelist

    total_num = 0
    for winfile in filelist:
        f = open(winfile,'r')
        num = int(f.readline().strip())
        print winfile,":", num
        total_num += num
        f.close()

    print "Total num of winfile:", total_num

    fo = open(outputfile, 'w')
    fo.write("%d\n" %total_num)
    for winfile in filelist:
        f = open(winfile, 'r')
        content = f.readlines()[1:]
        for line in content:
            fo.write(line)
    
    print "Output file:", outputfile

def merge_single_winfile(winbasedir, event_tag, outdir, databasedir):

    outputfile = os.path.join(outdir, event_tag)
    windir = os.path.join(winbasedir, event_tag)
    alllist = glob.glob( windir + "/*.win")

    print "In dir:", windir
    print "Total number of win file", len(alllist)

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
            fh = open(winfile)
            content = fh.readline()
            num_win = int(fh.readline().strip())
            if num_win > 0:
                filelist.append(winfile)
                n_used += 1
            else:
                #print "%s:%s %s %s %s" %(basename, sta, nw, loc, comp)
                n_unused += 1
        else:
            #print "%s:%s %s %s %s" %(basename, sta, nw, loc, comp)
            n_unused += 1

    print "Total number of winfile used:", len(filelist)
    fo.write("%d\n" %n_used)

    # write out the mereged file
    for winfile in filelist:
        basename = os.path.basename(winfile)
        sta_info = basename.split(".")
        sta = sta_info[0]
        nw = sta_info[1]
        loc = sta_info[2]
        comp = sta_info[3]
        obsd_fn = "%s.%s.%s.BH%s.sac" %(sta, nw, loc, comp[-1:])
        synt_fn = "%s.%s.MX%s.sac" %(sta, nw, comp[-1:])
        obsd_fn = os.path.join(databasedir, "OBSD_PROC", event_tag, obsd_fn)
        synt_fn = os.path.join(databasedir, "SYNT_PROC", event_tag, synt_fn)
        fwin = open(winfile, "r")
        content = fwin.readlines()
        content_write = content[1:]
        #print content_write
        fo.write("%s\n" %obsd_fn)
        fo.write("%s\n" %synt_fn)
        for line in content_write:
            fo.write(line)

if len(sys.argv) != 2:
    raise ValueError("Incorrect arg number")

# event name
eventname = sys.argv[1]

basedir = "/home/lei/DATA"
winbasedir = os.path.join(basedir, "window")
outdir = os.path.join(basedir, "window", "cmt3d_input")
databasedir = "/home/lei/DATA"

print "=============================\nEvent:", eventname
# first merge winfiles in different band
event_tag = eventname + "_27_60"
merge_single_winfile(winbasedir, event_tag, outdir, databasedir)

event_tag = eventname + "_60_120"
merge_single_winfile(winbasedir, event_tag, outdir, databasedir)

print "++++++++\nMerge..."
winfiledir = outdir
# merge different band together
merge_windfile(winfiledir, eventname)

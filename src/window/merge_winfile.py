# merge win files for different frequency band
import os
import glob

winfiledir = "/home/lei/Research/SOURCE_INVERSION/DATA/window/CMT3D_INPUT"

event = "010104J"

outputfile = os.path.join(winfiledir, "%s_all" %event)

search_pattern = os.path.join(winfiledir, "*%s*" %event)
filelist = glob.glob(search_pattern)

print search_pattern
print filelist

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

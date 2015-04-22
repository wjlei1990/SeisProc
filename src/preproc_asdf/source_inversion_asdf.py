from pycmt3d.cmt3d import Cmt3D
from pycmt3d.source import CMTSource
from pycmt3d.config import Config
from pycmt3d.window import *
from pycmt3d.const import PAR_LIST
from pycmt3d.const import NREGIONS

def create_asdf_dict(basedir, eventname, par_list, period_tag):
    asdf_dict = {}
    obsd_suffix = "proc_obsd_" + period_tag + ".h5"
    synt_suffix = "proc_synt_" + period_tag + ".h5"
    asdf_dict['obsd'] = os.path.join(basedir, "%s.%s" % (eventname, obsd_suffix))
    asdf_dict['synt'] = os.path.join(basedir, "%s.%s" % (eventname, synt_suffix))
    for deriv_type in par_list:
        asdf_dict[deriv_type] = os.path.join(basedir, "%s.%s.%s" % (eventname, deriv_type, synt_suffix))
    return asdf_dict

eventname = "010403A"
data_basedir = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/ASDF/proc"

cmtfile = "/ccs/home/lei/SOURCE_INVERSION/CMT_BIN/from_quakeml/" + eventname
cmtsource = CMTSource.from_CMTSOLUTION_file(cmtfile)

config = Config(9, dlocation=0.03, dmoment=2.0e23, ddepth=3.0,
                double_couple=False, station_correction=True,
                bootstrap=True, bootstrap_repeat=300,
                normalize_window=True)

data_con = DataContainer(PAR_LIST[0:9])

period_tag = "60_120"
flexwinfile = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/window/cmt3d_input/" + eventname + \
                "_" + period_tag + ".win"
asdf_file_dict = create_asdf_dict(data_basedir, eventname, PAR_LIST[0:9], period_tag)
print asdf_file_dict
data_con.add_measurements_from_asdf(flexwinfile, asdf_file_dict)


period_tag = "35_60"
flexwinfile = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/window/cmt3d_input/" + eventname + \
                "_" + period_tag + ".win"
asdf_file_dict = create_asdf_dict(data_basedir, eventname, PAR_LIST[0:9], period_tag)
print asdf_file_dict
data_con.add_measurements_from_asdf(flexwinfile, asdf_file_dict)


testcmt = Cmt3D(cmtsource, data_con, config)
testcmt.source_inversion()
#testcmt.plot_summary(figurename="test.png")

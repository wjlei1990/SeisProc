from pycmt3d.cmt3d import Cmt3D
from pycmt3d.source import CMTSource
from pycmt3d.config import Config
from pycmt3d.window import *
from pycmt3d.const import PAR_LIST
from pycmt3d.const import NREGIONS

eventname = "010403A"

cmtfile = "/ccs/home/lei/SOURCE_INVERSION/CMT_BIN/from_quakeml/" + eventname
cmtsource = CMTSource.from_CMTSOLUTION_file(cmtfile)
#print cmtsource.depth_in_m

config = Config(9, dlocation=0.03, dmoment=2.0e23, ddepth=3.0,
                double_couple=False, station_correction=True,
               bootstrap=True, bootstrap_repeat=300,
               normalize_window=True)

data_con = DataContainer(PAR_LIST[0:9])

cmt_suffix = "_60_120.win"
flexwinfile = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/window/cmt3d_input/" + eventname + cmt_suffix
data_con.add_measurements_from_sac(flexwinfile)

cmt_suffix = "_35_60.win"
flexwinfile = "/lustre/atlas/proj-shared/geo111/Wenjie/DATA_SI/window/cmt3d_input/" + eventname + cmt_suffix
data_con.add_measurements_from_sac(flexwinfile)

testcmt = Cmt3D(cmtsource, data_con, config)

testcmt.source_inversion()

#plot_stat = PlotUtil(data_container=data_con, cmtsource=cmtsource, nregions=NREGIONS,
#                    new_cmtsource=testcmt.new_cmtsource, bootstrap_mean=testcmt.par_mean,
#                    bootstrap_std=testcmt.par_std, var_reduction=testcmt.var_reduction)

#plot_stat.plot_inversion_summary()
#testcmt.plot_summary(figurename="test.png")

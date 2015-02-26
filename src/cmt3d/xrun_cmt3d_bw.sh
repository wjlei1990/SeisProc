#!/bin/sh
# Author: Hejun Zhu, hejunzhu@princeton.edu
# Princeton University, New Jersey, USA
# Last modified: Wed Aug 18 10:17:46 EDT 2010

# This script runs cmt3d several times 
# Each time uses different INVERSION parameters
# i.e. double couple; zero traces; 6,7 or 9 parameters

cmtdir="/home/lei/DATA/CMT_BIN"
windir="/home/lei/DATA/window/cmt3d_input"

parfile="INVERSION.PAR"
outdir="XFILES_RESULT_BW"
eventfile="XEVENTID"

ddelta='0.03   3.0   2.0e23'
weight_data='.true.'  # can be turned off 
weight='2  2  1  0.5  1.15  0.55  0.78'
#weight='1  1  1  0.5  0  0   0'
lampda='0.0'
write_new='.false.'
sc=".true."    # can be turned off 

while read line
do 
	cmtid=`echo $line | awk -F"_" '{print $NF}'`

	flexwin_out=$windir"/"$cmtid"_27_60.win"
	cmtfile=$cmtdir"/"$cmtid

	echo "cmtfile "$cmtfile

	if [ ! -d $outdir ]; then
		mkdir $outdir
	fi 
	if [ ! -f $flexwin_out ]; then 
		echo WRONG! No file $flexwin_out
		exit
	fi 
	if [ ! -f $cmtfile ]; then
		echo WRONG! NO $cmtfile
		exit 
	fi 


	for cmt_tag in 6p_ZT \
	       	       6p_ZT_DC \
	       	       7p_ZT \
                   7p_ZT_DC\
	               9p_ZT\
	               9p_ZT_DC
	do 
	
		new_cmtfn='CMTSOLUTION_'$cmtid'_'$cmt_tag
		parfile_ext=$parfile'.'$cmtid'.'$cmt_tag

		out='xcmt3d_'$cmtid'_'$cmt_tag'.out'

		if [ -f $parfile_ext ]; then 
			rm $parfile_ext
		fi 

		case $cmt_tag in 
			6p_ZT)
				npar=6
				zt=".true."
				dc=".false.";;
			6p_ZT_DC)
				npar=6
				zt=".true."
				dc=".true.";;
			7p_ZT)
				npar=7
				zt=".true."
				dc=".false.";;
			7p_ZT_DC)
				npar=7
				zt=".true."
				dc=".true.";;
			9p_ZT)
				npar=9
				zt=".true."
				dc=".false.";;
			9p_ZT_DC)
				npar=9
				zt=".true."
				dc=".true.";;
		esac 


		# Write INVERSION.PAR
		echo writing $parfile_ext...

		echo $cmtfile > $parfile_ext
		echo $new_cmtfn >> $parfile_ext
		echo "$npar              				-- npar: number of parameters inverted">> $parfile_ext
		echo "$ddelta            		--ddelta,ddepth,dmoment">> $parfile_ext
		echo $flexwin_out >> $parfile_ext
		echo "$weight_data       				-- weigh_data_files">> $parfile_ext
		echo "$weight            	--weights of data comp, az(exp), dist(exp)">> $parfile_ext
		echo "$sc                			--station_correction" >> $parfile_ext
		echo "$zt  $dc   $lampda    		--zero_trace,double_couple,lambda_damping">> $parfile_ext
		echo "$write_new         				-- write_new_syn">> $parfile_ext

		cat $parfile_ext > $parfile

		# Run cmt3d_flexwin
		echo running cmt3d_flexwin for $parfile_ext output to $out...
		./cmt3d_flexwin > $out
	
	done 

	# move the results to new directory
	mv CMTSOLUTION_$cmtid_*ZT*  $outdir
	mv INVERSION.PAR.$cmtid_*ZT*  $outdir
	mv xcmt3d_$cmtid_*ZT*.out  $outdir 
	cp $cmtfile $outdir"/CMTSOLUTION_"$cmtid"_"init

done < $eventfile 


#!/bin/bash

scriptname="plot_source_inv.py"

while read line
do
  echo
  echo "###"
	echo "event:" $line
  echo "###"
  echo "====================================="
	echo "python $scriptname $line ALL"
	python $scriptname $line ALL
  #echo "====================================="
	#echo "python $scriptname $line BW"
	#python $scriptname $line BW
  #echo "====================================="
	#echo "python $scriptname $line SW"
	#python $scriptname $line SW
done < XEVENTID


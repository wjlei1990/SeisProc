#!/bin/bash

scriptname="plot_source_inv.py"

while read line
do
	echo "event:" $line
	echo "python $scriptname $line ALL"
	python $scriptname $line ALL
	echo "python $scriptname $line BW"
	python $scriptname $line BW
	echo "python $scriptname $line SW"
	python $scriptname $line SW
done < XEVENTID


#!/bin/bash

scriptname="plot_source_inv.py"

while read line
do
	echo "event:" $line
	echo "python $scriptname $line"
	python $scriptname $line
done < XEVENTID


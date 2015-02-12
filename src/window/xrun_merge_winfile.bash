#!/bin/bash

scriptname="merge_all.py"

while read line
do
	echo "event:" $line
	echo "python $scriptname $line"
	python $scriptname $line
done < XEVENTID


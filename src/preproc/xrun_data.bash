#!/bin/bash

period_low=(35 60)
period_high=(60 120)

scriptname="process_data_rhea.py"

while read line
do
	echo "event:" $line
	echo "python $scriptname $line ${period_low[0]} ${period_high[0]}"
	python $scriptname $line ${period_low[0]} ${period_high[0]}
	echo "python $scriptname $line ${period_low[1]} ${period_high[1]}"
	python $scriptname $line ${period_low[1]} ${period_high[1]}
done < XEVENTID_ALL


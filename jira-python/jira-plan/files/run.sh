#!/bin/bash

# run.sh
# run the main program here if this directory has a single CSV file
pwd
csvs=$(ls *.csv | wc -w)
echo num CSV ${csvs}
if [ ${csvs} != 1 ]
then
	read -p "Fail.  Press a key to continue"
	exit 0
fi

csv=$(ls *.csv)
echo CSV ${csv}
python3 plan-update-jira.py ${csv}
# read -p "Done: Press a key to continue"

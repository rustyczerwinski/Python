#!/bin/bash

# run.sh
# run the main program here if this directory has a single CSV file

csvs=$(ls *.csv | wc -w)
csv=$(ls *.csv)

if [ ${csvs} != 1 ]
then
	echo "Need to have just one plan/CSV file, have ${csvs} (${csv})"
	read -p "Will not run.  Check plan files and try again" 
	exit 0
fi

python3 plan-update-jira.py ${csv}
read -p "Done"

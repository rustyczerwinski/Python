#! /usr/bin/env python

DELIMITER = "\t"
import sys
from jira_API import *

def getComponentCommandsFromFile(fileName):

    file = open(fileName,"r")
    # print("DEBUG File has:            (" + fileName + ")")

    line = file.readline().rstrip()
    # print("DEBUG first line " + str(line))
    # check whether Sprint defined in file, as first line
    if not line:
        return line

    componentChanges = dict()

    while len(line)>0:
        # print("DEBUG " +line)
        # print("DEBUG " +line[0])
        if "#" == line[0]:
            print("  (Commented out, not checking: " + line + ")")
        else:
            lineCSV = line.split(DELIMITER)
            # print('DEBUG line: ' + str(lineCSV))
            if len(lineCSV[0]) > 0:
                name = lineCSV[0]
                # print("DEBUG " + name)
                command = lineCSV[1]
                componentChanges[name]=command
        line=file.readline().rstrip()
    # print("DEBUG " + str(planfileStaffing))
    return componentChanges

commandFile = sys.argv[1]
project = sys.argv[2]
commands = getComponentCommandsFromFile(commandFile)
if not commands: print("Error getting commands from file " + commandFile)
updateProductComponents(project, commands)
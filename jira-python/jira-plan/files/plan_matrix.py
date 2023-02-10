#! /usr/bin/env python

# plan_matrix.py
# read plan file in format:
# [Sprint:<sprint>]
# ,<username1>,<username2>...         this include everyone that will work on any Epic in this file
# <Epic Jira ID>,<hours that username1 will work, "h" optional>,<hours for username2>....

SPRINT_LABEL = "SPRINT:"
STAFFING_DELIMITER = ","


def getStaffingFromCSV(fileName):

    # TODO add estimate to return plan
    planFile = open(fileName,"r")
    print("File has:            (" + fileName + ")")

    line = planFile.readline().rstrip()
    # print("DEBUG first line " + str(line))
    # check whether Sprint defined in file, as first line
    sprint = checkLineForSprint(line)
    # print("DEBUG value from Sprint: " + str(sprint))
    if sprint: # read next line as first staffing line
        line = planFile.readline().rstrip()
        # print("DEBUG Sprint found " + str(sprint) + "," + str(line))

    people = line.split(',')
    # print("DEBUG people in plan " + str(people))

    line = planFile.readline().rstrip()
    # print('DEBUG people: ' + str(people))

    planfileStaffing = dict()
    addedH = False
    while len(line)>0:
        # print("DEBUG " +line)
        # print("DEBUG " +line[0])
        if "#" == line[0]:
            print("  (Commented out, not checking: " + line + ")")
        else:
            lineCSV = line.split(STAFFING_DELIMITER)
            # print(' DEBUG line: ' + str(lineCSV))
            if len(lineCSV[0]) > 0:
                item = lineCSV[0]
                entry = 0
                itemStaffing = dict()
                for estimate in lineCSV[1:]:
                    entry += 1
                    if len(estimate)>0:
                        # make "h" optional in matrix, add if missing
                        if estimate[-1:].upper() == "H":
                            itemStaffing[people[entry]] = estimate
                        else:
                            addedH = True
                            itemStaffing[people[entry]] = estimate + "h"
                if len(itemStaffing) > 0:
                    planfileStaffing[item] = itemStaffing
                    print("  for " + item + ": " + str(planfileStaffing[item]))
                    if addedH: print("    FYI: added \"h\" to estimate(s)")
                else:
                    print("  for " + item + ": no staffing, taking no action. (" + line + ")")
        line=planFile.readline().rstrip()
    # print("DEBUG " + str(planfileStaffing))
    return planfileStaffing, sprint

def checkLineForSprint(line):
    # print("DEBUG Sprint check 1 " + str(line))
    if not line: return None

    # print("DEBUG Sprint check 2 " + str(line[0:len(SPRINT_LABEL)-1].upper()))
    if line[:len(SPRINT_LABEL)].upper() != SPRINT_LABEL: return None

    try:
        # print("DEBUG line split " + str(line.split(":")))
        sprint = line.split(":")[1].replace(STAFFING_DELIMITER,"")
        # print("DEBUG Sprint check try")
    except Exception as err:
        print("Error: Ignoring Sprint in line " + line + ", but not in expected format: Sprint:<name>")
        return None
    else:
        # print("DEBUG no exception return " + str(sprint))
        return sprint

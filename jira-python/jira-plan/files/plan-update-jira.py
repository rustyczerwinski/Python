
#! /usr/bin/env python

# read plan from CSV file
# for each Epic in file, read plan from Jira
# if staffing different in each, then update Jira
# report outcome: Epics updated, Epics already correct

# TODO import requests
# TODO import os
# TODO import json
import sys
from plan_matrix import getStaffingFromCSV
from plan_jira import * # getEpicPlan, update_resource_request_in_Jira, removeFromJiraEpicStaffingNotInPlan, addEpicStaffingPlanToJira, jiraEpicStaffingIsCorrect

if len(sys.argv) < 2:
    print("format: plan-update-jira.py <path for CSV staffing plan file>")
    exit(RuntimeError("Invalid command syntax"))

# get plan of record
print("===== reading plan file")
fileName = sys.argv[1]
correctStaffing, sprint = getStaffingFromCSV(fileName)

epicsFailedToUpdate = list()

for epicJiraID in correctStaffing.keys():
    print("===== checking Epic " + epicJiraID)
    if not jira_API.isInJira(epicJiraID):
        print("Error: Epic " + epicJiraID + " not found in Jira")
        break

    correctEpicStaffing = correctStaffing[epicJiraID]
    # print("DEBUG Checking Jira")

    epicEstimateFromJira, jiraEpicStaffing, jiraEpicStaffingFull = getJiraEpicPlan(epicJiraID)

    # here correctStaffing, from the plan file, has
    # [<epic>,[<person/username>:<estimate>,...]]

    # jira Epic staffing is : [<person1 username>:<estimate>, <person2 username>:<estimate>....]
    # above is to allow simple comparison with Correct Staffing

    # Jira staffing Full has more Jira fields and is:
    #     [<username1>: [resourceRequestJiraID: <>, summary:<>, estimate:<>], <username2>:[....] ]

    # save original Jira staffing for comparison and reporting after changes
    jiraEpicStaffingBefore = jiraEpicStaffing.copy() # might change so get "before" copy

    # now compare
    print("staffing:")
    print("  jira                           : " + str(jiraEpicStaffing))
    print("  correct staffing from plan file: " + str(correctStaffing[epicJiraID]))

    if jiraEpicStaffingIsCorrect(epicJiraID, jiraEpicStaffing, correctEpicStaffing):
        print("staffing already matches")
        jiraEpicStaffingFull = cleanUpEpicInJira(epicJiraID, sprint, correctEpicStaffing, epicEstimateFromJira, jiraEpicStaffingFull)
    else:
        print("staffing does not match, will attempt to correct")
        addToJiraMissingStaffingIncludedInPlan(epicJiraID, jiraEpicStaffing, correctEpicStaffing)
        removeFromJiraStaffingNotInPlan(epicJiraID, jiraEpicStaffing, jiraEpicStaffingFull, correctEpicStaffing)
        inJiraMatchPlanStaffingEstimates(epicJiraID, jiraEpicStaffing, jiraEpicStaffingFull, correctEpicStaffing)

        # update jira plan in memory after above changes
        epicEstimateFromJira, jiraEpicStaffing, jiraEpicStaffingFull = getJiraEpicPlan(epicJiraID)

        # check again
        print("  jira after changes: " + str(jiraEpicStaffing))
        if jiraEpicStaffingIsCorrect(epicJiraID, jiraEpicStaffing, correctEpicStaffing):
            print("staffing now matches")
            jiraEpicStaffingFull = cleanUpEpicInJira(epicJiraID, sprint, correctEpicStaffing, epicEstimateFromJira, jiraEpicStaffingFull)
        else:
            print("FAILED to update staffing in Jira, please update manually or contact tool support")
            print("    plan: " + str(correctEpicStaffing))
            print("    Jira after attempted changes: " + str(jiraEpicStaffing))
            epicsFailedToUpdate.append(epicJiraID)

print("===== Done")
if epicsFailedToUpdate:
    print("FAILED to update these Epics, see details above: " + str(epicsFailedToUpdate))
else:
    print("SUCCESS: Jira matches plan file for all Epics in plan file")
    otherEpics = getOtherJiraEpicsThisSprint(correctStaffing.keys(), sprint)
    if otherEpics: print("  (Note: other Epics in same project(s) and this Sprint, not in this plan - " + str(otherEpics))

#! /usr/bin/env python

import jira_API
import json
import utils

def getJiraEpicPlan(jiraEpicID):

    issue = jira_API.getIssue(jiraEpicID, "timetracking,subtasks")
    if not issue:
        return None

    # print("DEBUG " + str(issue))

    epicEstimate = getTimeEstimatefromIssueJSON(issue)
    epicStaffingSimple, epicStaffingFull = getStaffingFromResourceRequestsFromIssueJSON(issue)
    # print("DEBUG from Jira, staffing plan: " + str(epicStaffingSimple))
    return epicEstimate, epicStaffingSimple, epicStaffingFull

def getTimeEstimatefromIssueJSON(issue):
    try:
        estimate = issue['fields']['timetracking']['originalEstimate']
    except Exception:
        return 0
    else:
        return estimate

def getStaffingFromIssueJSON(issue):
    username = issue["assignee"]
    estimate = getTimeEstimatefromIssueJSON(issue)
    return {username: estimate}

def getStaffingFromResourceRequestsFromIssueJSON(issue):
    # TODO can combine staffing and full as [staffing: [], allData: [] ?

    # assume staffing requests are stored in Jira Epic Subtasks with specific type
    # Epic will have Subtask keys, but not the details needed
    # So use Epic to get keys, then use each key to get details from Jira

    subtasks = issue['fields']['subtasks']
    # print("DEBUG " + str(len(subtasks)) + ' subtasks')

    staffingSimple = dict()
    staffingFull = dict()
    for t in subtasks:
        type = t['fields']['issuetype']['name']
        # print('type: ' + type)
        if type == 'Resource Request':
            # print("DEBUG resource request: " + json.dumps(str(t)))
            staffingRequestJiraID = t['key']
            # print('get request ' + rtk)
            staffingRequestJSON = jira_API.getStaffingRequest(staffingRequestJiraID)
            if staffingRequestJSON:
                # print("DEBUG staffingRequestJSON: " + str(staffingRequestJSON))
                name = staffingRequestJSON['fields']['assignee']['name']
                estimate = staffingRequestJSON['fields']['timetracking']['originalEstimate']
                summary = staffingRequestJSON['fields']['summary']
            if name in staffingSimple.keys():
                # if this is duplicate staffing for this person, delete this duplicate (will check estimate and name later)
                removeStaffingRequestFromJira(staffingRequestJiraID)
            else:
                staffingSimple[name] = estimate
                staffingFull[name] = {"resourceRequestJiraID": staffingRequestJiraID, "summary": summary, "estimate": estimate}
            # print("DEBUG " + str(staffingSimple))
    return staffingSimple, staffingFull

def getIssueTimeEstimate(jiraID):
    r = jira_API.getIssueTimeEstimate(jiraID)
    if r:
        return  getTimeEstimatefromIssueJSON(r)
    else:
        print("Failed to get Jira time estimate for " + jiraID)
        return None

# take in Simple Epic staffing from Jira, with format matching correct staffing; Full staffing has Jira ID for resource Request, person which this is correcting
# update Jira and Simple staffing object
def updateStaffEstimateInJira(jiraEpicStaffingSimple, jiraEpicStaffingFull, correctEpicStaffing, person):
    jiraID = jiraEpicStaffingFull[person]["resourceRequestJiraID"]
    estimate = correctEpicStaffing[person]
    if jira_API.updateIssueTimeEstimate(jiraID, estimate):
        # print("DEBUG Updated estimate in Jira for " + person + " to " + estimate)
        jiraEpicStaffingSimple[person] = estimate
    return jiraEpicStaffingSimple

def getEpicEstimateFromStaffing(epicStaffingFull):
    epicEstimate = 0
    for username in epicStaffingFull:
        # print("DEBUG Staffing for estimate: " + str(epicStaffingFull[username]))
        # print("DEBUG " + str(epicStaffingFull[username])[:-1])
        jiraEstimate = epicStaffingFull[username]["estimate"]
        # print("DEBUG " + jiraEstimate)

        # strip off 'h' if there, to add estimates
        if jiraEstimate[-1:] == "h":
            thisEstimate = int(jiraEstimate[:-1])
        else:
            thisEstimate = int(jiraEstimate)

        epicEstimate += thisEstimate


    epicEstimate = str(epicEstimate) + "h"
    return epicEstimate

def removeFromJiraStaffingNotInPlan(epicJiraID, jiraEpicStaffing, jiraEpicStaffingFull, correctEpicStaffing):
    print("Scrubbing from Jira any staffing not needed")
    found = False
    staffingCopy = jiraEpicStaffing.copy()
    for username in staffingCopy.keys():
        if username not in correctEpicStaffing:
            found = True
            print("  Staffing for " + username + " deleting from Jira, not in plan")
            removeStaffingRequestFromJira(jiraEpicStaffingFull[username]["resourceRequestJiraID"])
            del jiraEpicStaffing[username]
    if not found: print("  Confirmed: Jira has the correct people")

    return jiraEpicStaffing

def removeStaffingRequestFromJira(resourceRequestJiraID):
    jira_API.deleteIssue(resourceRequestJiraID)


def addToJiraMissingStaffingIncludedInPlan(epicJiraID, jiraEpicStaffing, correctStaffing):
    print("Adding to Jira any staffing missing")
    # print("DEBUG adding Plan staffing to Jira")
    found = False
    # print("DEBUG " + str(jiraEpicStaffing))
    # print("DEBUG " + str(correctStaffing))
    for person in correctStaffing.keys():
        addPerson = False
        if not jiraEpicStaffing:
            addPerson = True
        elif person not in jiraEpicStaffing.keys():
            addPerson = True
        if addPerson:
            found = True
            if not jiraEpicStaffing:
                staffingCount = 1
            else:
                staffingCount = len(jiraEpicStaffing.keys()) + 1
            print("  Adding " + person + " to staffing in Jira")
            jiraEpicStaffing = addStaffToJiraEpicStaffing(epicJiraID, person, correctStaffing[person], jiraEpicStaffing)
        # else:
            # print("DEBUG " + person + " is in plan and Jira")

    if not found: print("  Jira has the correct people assigned")

    return jiraEpicStaffing

def jiraEpicStaffingIsCorrect(epicJiraID, jiraEpicStaffing, correctEpicStaffing):
    return (jiraEpicStaffing == correctEpicStaffing)

def addStaffToJiraEpicStaffing(epicJiraID, username, estimate, jiraEpicStaffing):
    # add this person to Epic staffing in Jira and in dictionary passed in

    if jira_API.createResourceRequestSubtask(epicJiraID, username, estimate):
        jiraEpicStaffing[username]=estimate
    else:
        print ("Error adding " + username + " to Epic " + epicJiraID)
    return jiraEpicStaffing

def addMissingStaffingToJira(epicJiraID, planEpicStaffing, jiraEpicStaffing):
    for person in planEpicStaffing.keys():
        if not jiraEpicStaffing[person]:
            # TODO include summary/name based n+1 on other requests
            jiraEpicStaffing = addStaffToJiraEpicStaffing(epicJiraID, person, planEpicStaffing[person], jiraEpicStaffing)

    return jiraEpicStaffing

def inJiraMatchPlanStaffingEstimates(epicJiraID, jiraEpicStaffing, jiraEpicStaffingFull, planEpicStaffing):
    print("Checking Jira for correct estimates for each person")
    corrected = False
    for person in planEpicStaffing.keys():
        if person in jiraEpicStaffing.keys():
            if planEpicStaffing[person] != jiraEpicStaffing[person]:
                if updateStaffEstimateInJira(jiraEpicStaffing, jiraEpicStaffingFull, planEpicStaffing, person):
                    jiraEpicStaffing[person] = planEpicStaffing[person]
                    jiraEpicStaffingFull[person]["estimate"] = planEpicStaffing[person] # need to update this?
                    print("  Updated estimate for " + person + " for Epic " + epicJiraID + " to " + planEpicStaffing[
                        person])
                    corrected = True
    if not corrected: print("  Confirmed that each staff estimate is correct")
    return jiraEpicStaffing

def inJiraupdateEpicEstimateFromStaffing(epicJiraID, currentEpicEstimate, jiraEpicStaffingFull):
    print("Checking total Epic estimate")
    estimateFromStaffing = getEpicEstimateFromStaffing(jiraEpicStaffingFull)
    if estimateFromStaffing != currentEpicEstimate:
        if jira_API.updateIssueTimeEstimate(epicJiraID, estimateFromStaffing):
            print("  Updated Epic estimate in Jira, based on staffing, to " + estimateFromStaffing)
        else:
            print("Error updating Epic estimate")
            return False
    else:
        print("  Confirmed Epic total estimate is correct")
    return True

def correctStaffingJiraNames(epicJiraID, correctEpicStaffing, jiraEpicStaffingFull):
    print("Checking staffing issue names")
    corrected = False
    numStaff = len(correctEpicStaffing.keys())
    # print("DEBUG numStaff:" + str(numStaff))
    namesShouldHave = list()
    namesJiraHas = dict()
    for s in range(1,numStaff+1):
        # print("DEBUG adding to list of resource item names we should have: " + str(s))
        namesShouldHave.append("Resource " + str(s))
    for username in jiraEpicStaffingFull.keys():
        if username in namesJiraHas.keys():
            # name duplicated in Jira, so change this one
            staffingJiraID = jiraEpicStaffingFull[username]["resourceRequestJiraID"]
            if jira_API.updateIssueName(staffingJiraID, "Change this name (for " + username + ")"):
                print("Staffing item " + staffingJiraID + " has duplicate name, updating")
                corrected = True
        else:
            namesJiraHas[jiraEpicStaffingFull[username]["summary"]] = jiraEpicStaffingFull[username]["resourceRequestJiraID"]

    if namesShouldHave == namesJiraHas.keys():
        print("Staffing Jira items have correct names")
        return True

    namesMissing = list()

    for nameShouldHave in namesShouldHave:
        if nameShouldHave not in namesJiraHas:
            # print("DEBUG Should have in Jira but do not: " + nameShouldHave)
            namesMissing.append(nameShouldHave)

    # print("DEBUG staffing item names/summaries - should have " + str(namesShouldHave))
    # print("DEBUG staffing item names/summaries - Jira has " + str(namesJiraHas))
    # print("DEBUG staffing item names/summaries - missing " + str(namesMissing))

    for nameJiraHas in namesJiraHas:
        if nameJiraHas not in namesShouldHave:
            rightNameAvailable = namesMissing.pop()
            # print("DEBUG Jira has invalid name (" + nameJiraHas + ") changing to (" + rightNameAvailable + ") (available names remaining: " + str(rightNameAvailable))
            staffingJiraID = namesJiraHas[nameJiraHas]
            if jira_API.updateIssueName(staffingJiraID, rightNameAvailable):
                print("Staffing item " + staffingJiraID + " name updated to " + rightNameAvailable)
                corrected = True
            else:
                print("Failed to update name for staffing item " + staffingJiraID)
    if not corrected: print("  Confirmed that Jira has the right staffing item names")
    return True

# this is to ensure that the items/fields based on simple staffing are correct
# including Epic time estimate, then names for individual staffing Jira Issues
# if the plan included Sprint, ensure that Epic is assigned
def cleanUpEpicInJira(epicJiraID, sprint, correctEpicStaffing, epicEstimateInJira, jiraEpicStaffingFull):
    inJiraupdateEpicEstimateFromStaffing(epicJiraID, epicEstimateInJira, jiraEpicStaffingFull)
    correctStaffingJiraNames(epicJiraID, correctEpicStaffing, jiraEpicStaffingFull)
    if not assignEpicToSprint(epicJiraID, sprint):
        print("Failed to assign " + epicJiraID + " to sprint " + sprint)

def assignEpicToSprint(epicJiraID, sprint):
    print("Checking Epic assigned to sprint " + sprint)
    return jira_API.addLabelToIssue(epicJiraID,sprint)

# the plan might not include all Epics that have been assigned to this Sprint.
# For the projects represented in the plan, find in Jira and return other Epics assigned to this Sprint
def getOtherJiraEpicsThisSprint(knownEpics, Sprint):
    epicCSVList = ""
    projectCSVList = ""
    for epic in knownEpics:
        epicCSVList = utils.includeInCSV(epicCSVList,epic)
        projectCSVList = utils.includeInCSV(projectCSVList,jira_API.getProjectFromJiraID(epic))

    # TODO jql="project=NXTEST+AND+type=Epic+AND+labels=23.01+AND+key+not+in+(NXTEST-1188)"
    jql = "project+in+(" + projectCSVList + ")+AND+type=Epic+AND+labels=" + Sprint + "+AND+key+not+in+(" + epicCSVList + ")"
    # print("DEBUG get others " + epicCSVList + ":" + projectCSVList + " jql = " + jql)
    epics = jira_API.getIssuesKeys(jql=jql)
    # print("DEBUG get others " + str(epics))
    if epics:
        return epics
    else:
        return None
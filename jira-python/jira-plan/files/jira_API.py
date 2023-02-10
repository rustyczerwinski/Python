#! /usr/bin/env python

# jira_API.py
# Wrap Jira API calls, using API library and
# returning True/False, dictionaries, or other simple fields as appropriate

import os
import json
import sys
import api
import requests
import utils

user = os.environ['JIRA_USER']
pw = os.environ['JIRA_PW']
jiraAPIV2URL = "https://<TODO jira instance>/rest/api/2/"

def isInJira(jiraID):
    r= getIssue(jiraID,"summary")
    # print("DEBUG " + jiraID + " " + str(r))
    return (r is not None)

def getIssue(jiraID, csvFields=""):
    url = jiraAPIV2URL + "issue/" + jiraID
    if [ csvFields != "" ]:
        url = url +  "?fields=" + csvFields
    r = api.get(url, user, pw, swallowError=True)
    return r

    # TODO error handling


def getIssues(csvFields="", jql=""):
    url = jiraAPIV2URL + "search"
    if [csvFields != ""]:
        url = url + "?fields=" + csvFields
    if [jql != ""]:
        if [csvFields != ""]:
            url = url + "?"
        else:
            url = url + "&"
        url = url + "jql=" + jql

    r = api.get(url, user, pw) # TODO, swallowError=True)
    return r

def getIssuesKeys(jql):

    url = jiraAPIV2URL + "search"
    # jql="project=NXTEST+AND+type=Epic+AND+labels=23.01+AND+key+not+in+(NXTEST-1188)"
    # jql="key=NXTEST-1188"
    if [jql != ""]:
        url = url + "?fields=key&jql=" + jql # ensure minimum keys
    else:
        print("Error getting Issues from Jira: jql must filter issues, filter provided = " + jql)
        return None

    r = api.get(url, user, pw, swallowError=True) # TODO, swallowError=True)
    # print("DEBUG get str  " + url + " " + str(r) )
    # print("DEBUG get Issues " + url + " " + " issues " + str( r["issues"]))
    keys = list()
    if r:
        for epic in r["issues"]:
            # print("DEBUG issues " + str(r) + " " + str(epic))
            keys.append(epic["key"])
            # print("DEBUG issues " + str(r))
    return keys


def getProjectFromJiraID(jiraID):
    return jiraID.split("-")[0]

def createResourceRequestSubtask(parentJiraID, username, estimate):
    # TODO could figure out summary/name based on other tasks
    project = getProjectFromJiraID(parentJiraID)
    payload = '{ "fields": { ' + \
        '"project": { "key": "' + project + '" },' + \
        '"reporter" : { "name": "' + user + '" },' + \
        '"issuetype": { "name": "Resource Request", "subtask": "true" },' + \
        '"summary": "Resource ' + username + '",' + \
        '"assignee": { "name": "' + username + '" },' + \
        '"parent":{"key": "' + parentJiraID + '" },' + \
        '"timetracking": { "originalEstimate": "' + estimate + '" }' + \
        '}}'
    url = jiraAPIV2URL + "issue"
    result = api.post(url, payload, user, pw)
    if not result:
        print("Error creating Resource Subtask")

    return result

def addLabelToIssue(jiraID, label):
    payload = '{"update":{"labels":[{"add":"' + label + '"}]}}'
    url = jiraAPIV2URL + "issue/" + jiraID

    result = api.put(url, payload, user, pw)
    if not result:
        # print("DEBUG Error Adding Label to Issue " + url + " " + payload + " " + str(result))
        pass

    return result

def getStaffingRequest(jiraID):
    r = getIssue(jiraID, csvFields="assignee,summary,timetracking")

    if not r:
        print("Error getting Staffing Request " + jiraID + " from Jira. ")
    return r

def getIssueStaffing(jiraID):
    r = getIssue(jiraID,"assignee,summary,timetracking")
    if not r:
        print("Error getting Staffing for " + jiraID + " from Jira.")
    return r

def updateIssueName(jiraID, name):
    payload = "{ \"key\": \"" + jiraID + "\", \"fields\": { \"summary\": \"" + name + "\" } } "
    url=jiraAPIV2URL + "issue/" + jiraID
    # print("DEBUG " + url)
    # print("DEBUG " + payload)
    if api.put(url, payload, user, pw):
        # print("DEBUG Updated issue " + jiraID + " name/summary to " + name)
        return True
    else:
        # print("DEBUG Failed to update Issue Name " + jiraID, name)
        return False

def updateIssueTimeEstimate(jiraID, estimate):
    payload = "{ \"key\": \"" + jiraID + "\", \"fields\": { \"timetracking\": { \"originalEstimate\": \"" + estimate + "\" } } } "
    url=jiraAPIV2URL + "issue/" + jiraID
    # print("DEBUG " + url)
    # print("DEBUG " + payload)
    if api.put(url, payload, user, pw):
        print("Updated issue " + jiraID + " time estimate (timetracking/originalEstimate) to " + estimate)
        return True
    else:
        print("Update failed")
        return False

    return api.put(url, payload, user, pw) # True/Faluse

def deleteIssue(jiraID):
    url = jiraAPIV2URL + "issue/" + jiraID
    return api.delete(url, user, pw)


#! /usr/bin/env python

from jira_API import *

allComponents = getProjectComponentsIDsNames("DONTAP")
for name in allComponents.keys():
    print("" + name + "," + str(allComponents[name]))
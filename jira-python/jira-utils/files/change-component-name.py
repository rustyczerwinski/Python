#! /usr/bin/env python

from jira_API import *

curName = ""
newName = ""
if len(sys.argv) < 4:
    print("format: change-component-name <project> <current name> <new name>")
    exit(RuntimeError("Invalid command syntax"))
else:
    project= sys.argv[1]
    curName = sys.argv[2]
    newName = sys.argv[3]

if changeProjectComponentName(project, curName, newName):
    print("DEBUG success")
else:
    print("DEBUG failed")

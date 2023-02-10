#! /usr/bin/env python
# Basic HTTP operations, GET, PUT, POST, DELETE
# For operations to GET data, return Python JSON dictionaries
# For operations that effect the destination data but do not need to GET/read data, return True/False
# for any operations, optionally swallow error (return empty) or raise error

import requests
import json

SUCCESS_STATUS="SUCCESS"
FAILURE_STATUS="FAILURE"
SIMPLE_STATUS={200: SUCCESS_STATUS, 204: SUCCESS_STATUS, "200": "SUCCESS", "201": "SUCCESS", "202": "SUCCESS", "203": "SUCCESS", "204": "SUCCESS", "205": "SUCCESS", 404: FAILURE_STATUS, 405: FAILURE_STATUS}

putHeaders = { "Content-Type": "application/json", "Accept": "application/json" }
getHeaders = { "Content-Type": "application/json" }
verify="/usr/local/share/ca-certificates/local.crt"

def getSimpleStatus(code):
    if int(code/100) == 2:
        return SUCCESS_STATUS
    else:
        return FAILURE_STATUS

def put(url,payload, user, pw):
    r = requests.put(
        url=url,
        data=payload,
        headers=putHeaders,
        verify=verify,
        auth=(user, pw) )

    if getSimpleStatus(r.status_code) == SUCCESS_STATUS:
        return True # return simple True/False
    else:
        print("Error with PUT request " + str(r.status_code) + " " + r.text)
        print(url)
        print(payload)
        print(user)
        return False

def post(url,payload, user, pw):
    r = requests.post(
        url=url,
        data=payload,
        headers=putHeaders,
        verify=verify,
        auth=(user, pw) )

    # print("DEBUG POST " + url + payload + user + str(r) + str(r.status_code))
    if getSimpleStatus(r.status_code) == SUCCESS_STATUS:
        return True # return simple True/False
    else:
        print("Error with POST request " + str(r.status_code) + " " + r.text)
        print(url)
        print(payload)
        print(user)
        return False


def get(url, user, pw, swallowError=False):
    # print("DEBUG GET " + str(swallowError))
    try:
        # print("DEBUG in try")
        r = requests.get(
            url=url,
            headers=getHeaders,
            verify=verify,
            auth=(user, pw)
        )
    except Exception as err:
        # print("DEBUG Error " + str(err))
        if swallowError:
            return None
        else:
            raise(err)
    else:
        if r:
            # print("DEBUG in try after get " + str(r.status_code))
            if getSimpleStatus(r.status_code) != SUCCESS_STATUS:
                if not swallowError:
                    print("Error in GET request to " + url)
                    raise requests.HTTPError
            else:
                return r.json()

        return None

def delete(url, user, pw):
    r = requests.delete(
        url=url,
        verify=verify,
        auth=(user, pw)
    )
    # print("DEBUG " + str(r.status_code))
    # print("DEBUG " + r.text)
    if getSimpleStatus(r.status_code) == SUCCESS_STATUS:
        return True
    else:
        print("Error deleting")
        return False


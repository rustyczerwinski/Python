#! /usr/bin/env python

# manage comma-separated-values list with only distinct values
def includeInCSV(list, value):
    # print("DEBUG include in CSV " + str(list) + ":" + str(value))
    if list.find(value) == -1:
        if list != "":
            list += ","
        list += value

    # print("DEBUG include in CSV " + str(list) + ":" + str(value))
    return list


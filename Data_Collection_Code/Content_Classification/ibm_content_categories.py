import csv
import re
from operator import itemgetter
import random


def jsonContentCategories():
    """
    Parses the IBM Cloud content categories from a local txt file and returns a nested dictionary (ugly, but effective).

    Returns:
        Dictionary -- Nested dictionary of content categories.
    """
    
    catArr = []
    with open("ibm_content_categories.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for i, line in enumerate(reader):
            if i == 0:
                continue
            linef = line[0]
            linef = linef + ";"  # in case last line is not semicolon
            linef = linef.replace(";;;;", ";")
            linef = linef.replace(";;;", ";")
            linef = linef.replace(";;", ";")
            category = re.findall(r'(.+?);', linef)
            catArr.append(category)

    catArr.sort(key=itemgetter(0))
    level0 = {}

    for i, value in enumerate(catArr):
        if len(value) == 1:
            if value[0] not in level0.keys():
                level0[value[0]] = []
                catArr.pop(i)

    for item in catArr:
        if len(item) >= 2:
            exists = False
            for i, value in enumerate(level0[item[0]]):
                if item[1] in value.keys():
                    exists = True
            if not exists:
                level0[item[0]].append({item[1]: []})

    for item in catArr:
        if len(item) >= 3:
            index = 0
            for i, value in enumerate(level0[item[0]]):
                if item[1] in value.keys():
                    index = i
            exists = False
            if len(level0[item[0]][index][item[1]]) == 0:
                level0[item[0]][index][item[1]].append({item[2]: []})
            else:
                for i, value in enumerate(level0[item[0]][index][item[1]]):
                    if item[2] in value.keys():
                        exists = True
                if not exists:
                    level0[item[0]][index][item[1]].append({item[2]: []})

    for item in catArr:
        if len(item) >= 4:
            index1 = 0
            index2 = 0
            for i, value in enumerate(level0[item[0]]):
                if item[1] in value.keys():
                    index1 = i
            for i, value in enumerate(level0[item[0]][index1]):
                for i, value in enumerate(level0[item[0]][index1][value]):
                    if item[2] in value.keys():
                        index2 = i

            exists = False
            l3arr = level0[item[0]][index1][item[1]][index2][item[2]]
            if len(l3arr) == 0:
                level0[item[0]][index1][item[1]][index2][item[2]].append({item[3]: []})
            else:
                for i, value in enumerate(l3arr):
                    if item[3] in value.keys():
                        exists = True
                if not exists:
                    level0[item[0]][index1][item[1]][index2][item[2]].append({item[3]: []})

    for item in catArr:
        if len(item) >= 5:
            index1 = 0
            index2 = 0
            index3 = 0
            index4 = 0
            for i, value in enumerate(level0[item[0]]):
                if item[1] in value.keys():
                    index1 = i
            for i, value in enumerate(level0[item[0]][index1]):
                for i, value in enumerate(level0[item[0]][index1][value]):
                    if item[2] in value.keys():
                        index2 = i
                    for i, value in enumerate(level0[item[0]][index1][item[1]]):
                        if item[2] in value.keys():
                            index3 = i
                    for i, value in enumerate(level0[item[0]][index1][item[1]][index3][item[2]]):
                        if item[3] in value.keys():
                            index4 = i

            exists = False
            l4arr = level0[item[0]][index1][item[1]
                                            ][index3][item[2]][index4][item[3]]
            if len(l4arr) == 0:
                level0[item[0]][index1][item[1]][index3][item[2]][index4][item[3]].append({item[4]: []})
            else:
                for i, value in enumerate(l3arr):
                    if item[3] in value.keys():
                        exists = True
                if not exists:
                    level0[item[0]][index1][item[1]][index3][item[2]][index4][item[3]].append({item[4]: []})

    return level0


def getKeys(dic):
    """
    Recursively finds all nested keys for a given higher-level key in the category dictionary.

    Returns:
        List -- List of dictionary keys.
    """
    
    localKeys = []
    if isinstance(dic, list):
        for item in dic:
            localKeys = [*localKeys, *getKeys(item)]
    elif isinstance(dic, str):
        localKeys.append(dic)
    else:
        for k, v in dic.items():
            localKeys.append(k)
            localKeys = [*localKeys, *getKeys(v)]
    return localKeys


def getCategories(l0keyP="", testTypeP=0):
    """
    Depending on the provided testType, this function finds random child keys, which we use to generate Twitter hashtags. For our evaluation we mainly used testType 2 or 3.

    Returns:
        List -- List of two lists. First, the provided or random l0key, second, depending on the test typ, its nested children keys.
    """

    # The content categories consist of 5 levels and we start counting at level 0                                       #
    #                                                                                                                   #
    #                                                                                                                   #
    # l0key:        "art and entertainment"                                                                             #
    #                                                                                                                   #
    # testType:                                                                                                         #
    #               0 -> returns [l0key] AND [l0key]                                                                    #
    #               1 -> returns [l0key] AND [l0key children]                                                           #
    #               2 -> returns [l0key, random l1key for l0key] AND [l1key children (l2)]                              #
    #               3 -> returns [l0key, random l1key for l0key, random l2key for l1key] AND [l2key children (l3)]      #
    #                                                                                                                   #

    l0key = l0keyP
    testType = testTypeP
    categories = jsonContentCategories()
    test = [[], []]

    # if(testType == -1):
    #    testType = randint(0,3) # Gen random valid test type

    if l0key == "":
        l0key = random.choice(list(categories))  # Gen random valid l0key

    if testType == 0:
        test[0].append(l0key)
        ###
        test[1].append(l0key)

    if testType == 1:
        test[0].append(l0key)
        ###
        test[1] = [*test[1], *(getKeys(categories[l0key]))]

    if testType == 2:
        test[0].append(l0key)
        l1keys = []
        for dic in categories[l0key]:
            l1keys.append(next(iter(dic)))
        # Gen random valid l1key for l0key
        l1keyIndex = random.choice(range(len(l1keys)))
        test[0].append(l1keys[l1keyIndex])
        ###
        test[1] = [*test[1], *
                   (getKeys(categories[l0key][l1keyIndex][l1keys[l1keyIndex]]))]
        if test[1] == []:  # random l1key doesn't have any children
            # try all l1keys
            for i in range(len(l1keys)):
                l1children = getKeys(categories[l0key][i][l1keys[i]])
                if l1children != []:
                    test[0][1] = l1keys[i]
                    test[1] = [*test[1], *l1children]
                    break
        # still none -> go recursive (guaranteed deterministic, because there are valid keys)
        if test[1] == []:
            test = getCategories(testTypeP=testTypeP)

    if(testType == 3) and (l0keyP == ""):  # OK -> provided not l0key
        test2 = getCategories(testTypeP=2)
        l0key = test2[0][0]
        l1key = test2[0][1]

        l1keyIndex = 0
        for dic in categories[l0key]:
            if next(iter(dic)) == l1key:
                break
            else:
                l1keyIndex += 1

        l2keys = []
        for dic in categories[l0key][l1keyIndex][l1key]:
            l2keys.append(next(iter(dic)))
        if l2keys == []:
            # SHOULD NEVER HAPPEN (no l2 children for all l1keys for given l0key)
            return test
        # Gen random valid l2key for l1key
        l2keyIndex = random.choice(range(len(l2keys)))
        test[0] = [*(test2[0]), l2keys[l2keyIndex]]
        l2key = test[0][2]
        l2keyIndex = 0
        for dic in categories[l0key][l1keyIndex][l1key]:
            if next(iter(dic)) == l2key:
                break
            else:
                l2keyIndex += 1
        ###
        test[1] = [
            *test[1], *(getKeys(categories[l0key][l1keyIndex][l1key][l2keyIndex][l2key]))]
        # no l2key children -> go recursive (guaranteed deterministic, because there are valid keys)
        if test[1] == []:
            test = getCategories(testTypeP=testTypeP)

    if(testType == 3) and (l0keyP != ""):  # NOT OK -> provided l0key
        raise ValueError(
            "You cannot provide a l0key when running a type 3 test")

    return test


# print(getCategories(testTypeP=0))
# print(getCategories(testTypeP=1))
#print(getCategories(l0keyP="science", testTypeP=2))
# print(getCategories(testTypeP=2))
# print(getCategories(testTypeP=3))

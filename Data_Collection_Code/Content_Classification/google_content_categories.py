import re
from operator import itemgetter
import random


def jsonContentCategories():
    """
    Parses the Google Cloud content categories from a local txt file and returns a nested dictionary (ugly, but effective).

    Returns:
        Dictionary -- Nested dictionary of content categories.
    """

    f = open("google_content_categories.txt", "r")
    catArr = []
    for line in f:
        category = re.findall(r'<td>(.+?)</td>', line)

        if len(category) == 1:
            cat = category[0].replace("&amp;", "&")  # readability
            cat = cat.replace("&#39;", "'")  # readability
            cat = cat[1:]
            arr = cat.split("/")
            catArr.append(arr)

    catArr.sort(key=itemgetter(0))
    level0 = {}
    for item in catArr:
        if len(item) == 1 and item[0] not in level0.keys():
            level0[item[0]] = []

    for item in catArr:
        if len(item) == 2:
            level0[item[0]].append({item[1]: []})

    for item in catArr:
        if len(item) == 3:
            for i, value in enumerate(level0[item[0]]):
                if item[1] in value.keys():
                    level0[item[0]][i][item[1]].append(item[2])

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
    Depending on the provided testType, this function finds random child keys, which we use to generate Twitter hashtags. For our evaluation we mainly used testType 2.

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
    #                                                                                                                   #

    l0key = l0keyP
    testType = testTypeP
    categories = jsonContentCategories()
    test = [[], []]

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

    return test


# print(getCategories(testTypeP=0))
# print(getCategories(testTypeP=1))
#print(getCategories(l0keyP="Arts & Entertainment", testTypeP=2))
# print(getCategories(testTypeP=2))

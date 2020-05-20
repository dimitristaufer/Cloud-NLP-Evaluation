import sys
sys.path.append('../')
sys.path.append('../..')
import json
import time
import random
from mongo_connect import Connect
import get_test_sentences as entitySentenceFinder

# Example query at https://petscan.wmflabs.org:
#
# SELECT DISTINCT ?wikidata_page ?label_en ?date_modified
# WHERE
# {
#  # Person: Q5
#  # Place (city): Q515
#  # Organization: Q43229
#  # Event: Q1656682 or Q1190554
#  # Product: Q2424752
#  ?wikidata_page wdt:P31 wd:Q2424752;
#  schema:dateModified ?date_modified.
#  ?wikidata_page rdfs:label ?label_en filter (lang(?label_en) = "en").
#  BIND (now() - ?date_modified as ?date_range)
#  FILTER (?date_range < 91) # edited within the last 90 days
# }
# LIMIT 20000

### Mongo DB Init ###
connection = Connect.get_connection()

db = connection.entityRecognition
groundTruth = db.groundTruth

# tested entities
groundTruthTE = db.groundTruthTE
###               ###

print("... Initializing ...")

# https://petscan.wmflabs.org
# article edited in the last 90 days (23/03/2020) from Wikidata
personEntities = "./query.wikidata.org/Person.json"
# article edited in the last 90 days (23/03/2020) from Wikidata
locationEntities = "./query.wikidata.org/Location.json"
# article edited in the last 90 days (23/03/2020) from Wikidata
organizationEntities = "./query.wikidata.org/Organization.json"

fPerson = open(personEntities)
fLocation = open(locationEntities)
fOrganization = open(organizationEntities)

# load the entire file, because these JSON files are not very large
dataPerson = json.load(fPerson)
dataLocation = json.load(fLocation)
dataOrganization = json.load(fOrganization)

print("... Initialized ...")
print("... Entity count 'Person':           "+str(len(dataPerson)))
print("... Entity count 'Location' :           "+str(len(dataLocation)))
print("... Entity count 'Organization':     "+str(len(dataOrganization)))

def getRandomEntities():
    """
    Selects a random Person, Location, and Organization that has not been tested before.
    """
    
    excludedEntities = []
    for doc in groundTruthTE.find():  # exclude test entities that have already been used (the collection can be emptied after 7 days or so)
        excludedEntities.append(doc["label_en"])

    randomPerson = random.choice(dataPerson)
    while randomPerson["label_en"] in excludedEntities:
        randomPerson = random.choice(dataPerson)

    randomLocation = random.choice(dataLocation)
    while randomLocation["label_en"] in excludedEntities:
        randomLocation = random.choice(dataLocation)

    randomOrganization = random.choice(dataOrganization)
    while randomOrganization["label_en"] in excludedEntities:
        randomOrganization = random.choice(dataOrganization)

    # Replace the '_' character of multi word Wikipedia titles
    randomPersonTitle = randomPerson["label_en"].replace("_", " ")
    randomLocationTitle = randomLocation["label_en"].replace("_", " ")
    randomOrganizationTitle = randomOrganization["label_en"].replace("_", " ")

    return {
        "Person": randomPersonTitle,
        "Location": randomLocationTitle,
        "Organization": randomOrganizationTitle
    }


def generateGroundTruth():
    """
    Retrieves as many sentences as possible from online news articles containing a specified named entity of type Person, Location, or Organization.
    """
    
    randomEntities = getRandomEntities()
    #print(json.dumps(randomEntities, indent=4, sort_keys=False))
    for entityType in randomEntities:
        entity = randomEntities[entityType]
        sentenceData = entitySentenceFinder.getTestSentences(
            entity, entityType)
        if len(sentenceData["sentences"]) > 0:
            upFilter = {"entity": {"$eq": entity}}
            upUpdate = {"$setOnInsert": {"entity": sentenceData["entity"],
                                         "entityType": sentenceData["entityType"]},
                        "$addToSet": {"sentences": {"$each": sentenceData["sentences"]}}}
            groundTruth.update_many(upFilter, upUpdate, upsert=True)
            print(u'\u2705' + " added " +
                  str(len(sentenceData["sentences"])) + " entity sentences to database ...")
        else:
            print(u'\u274C' + " did not found any useful sentences ...")
        # add to TE (tested entities)
        groundTruthTE.insert_one({"label_en": entity})
        print("... added '" + entity + "' to TE (tested entities) ...")
        sleepTime = random.randrange(30, 120)  # sleep 0.5 to 2 minutes
        print("... sleeping " + str(sleepTime) + " seconds ...")
        time.sleep(sleepTime)

# Usage Example:

#while 1:
#    generateGroundTruth()

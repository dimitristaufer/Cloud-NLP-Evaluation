import sys
sys.path.append('../')
sys.path.append('../..')
from datetime import datetime
import time
import re
import hashlib
from random import randrange
from mongo_connect import Connect
import google_content_categories as gCategories
import ibm_content_categories as iCategories
import get_tweets as TwitterSearch
import read_article as TwitterNewsReader

### Mongo DB Init ###
connection = Connect.get_connection()

db = connection.contentClassification
googleGroundTruth = db.googleGroundTruth
ibmGroundTruth = db.ibmGroundTruth

googleGroundTruthTC = db.googleGroundTruthTC # tested categories
ibmGroundTruthTC = db.ibmGroundTruthTC # tested categories
###               ###

def getRandomTests(provider):
    """Retrieves a test category and hashtag (level 1+) categories that have not been tested before (stored in XX..TC MongoDB)

    Arguments:
        provider {String} -- Provider name, either 'Google' or 'Ibm'

    Returns:
        Dictionary -- A test category and hashtag (level 1+) categories
    """
    
    excludedL0 = []
    if provider == "Google":
        for doc in googleGroundTruthTC.find(): # exclude test Categories (l0 categories) that have already been used (the collection can be emptied after 7 days or so)
            excludedL0.append(doc["test_category"])
        
        randomGTest = {
            "testCategory" : "l0",
            "hashtagCategories" : []
        }
        
        retries = 9999 # simple way to stop, when all keys have been tested
        while 1:
            gQuery = gCategories.getCategories(testTypeP=1)
            if retries > 0:
                if len(gQuery[1]) > 0 and (gQuery[0][0] not in excludedL0): # l1 children found for random l0 key
                    randomGTest["testCategory"] = gQuery[0][0]
                    randomGTest["hashtagCategories"] = gQuery[1]
                    break
            else:
                print("... Google - maximum number of retries exceeded ...")
                sys.exit()
            retries -= 1
        
        return randomGTest
        
    if provider == "Ibm":
        for doc in ibmGroundTruthTC.find(): # exclude test Categories (l0 categories) that have already been used (the collection can be emptied after 7 days or so)
            excludedL0.append(doc["test_category"])
        excludedL0 = list(set(excludedL0))
        
        randomWTest = {
            "testCategory" : "l0",
            "hashtagCategories" : []
        }
        
        retries = 9999 # simple way to stop, when all keys have been tested
        while 1:
            wQuery = iCategories.getCategories(testTypeP=1)
            if retries > 0:
                if len(wQuery[1]) > 0 and (wQuery[0][0] not in excludedL0): # l1 children found for random l0 key
                    randomWTest["testCategory"] = wQuery[0][0]
                    randomWTest["hashtagCategories"] = wQuery[1]
                    break
            else:
                print("... Ibm - maximum number of retries exceeded ...")
                sys.exit()
            retries -= 1

        return randomWTest
    
def generateHashtags(randomTests):
    """Generates a hashtag from a level 1+ category name using Regular Expressions and other rules.

    Arguments:
        randomTests {Dictionary} -- A test category and hashtag (level 1+) categories

    Returns:
        Dictionary -- The input dictionary with added hashtag names
    """
    
    tests = randomTests
    hashtags = []
    for i in range(len(tests["hashtagCategories"])):
        unmodCat = tests["hashtagCategories"][i]
        tests["hashtagCategories"][i] = tests["hashtagCategories"][i].replace(re.sub('([^>]+)', '', tests["hashtagCategories"][i]), "") # remove texts in brackets, e.g. (E.12)
        tests["hashtagCategories"][i] = tests["hashtagCategories"][i].replace(" ", "") # remove spaces
        tests["hashtagCategories"][i] = tests["hashtagCategories"][i].split("&") # split words by '&' (beacause these can be considered as two separate words)
        for j in range(len(tests["hashtagCategories"][i])): # since we now have arrays of one or more words
            tests["hashtagCategories"][i][j] = re.sub(r'[^A-Za-z]', '', tests["hashtagCategories"][i][j]) # remove non alphabetic characters
            tagAndCat = {
                "hashtag" : tests["hashtagCategories"][i][j].lower(),
                "category" : unmodCat
            }

            hashtags.append(tagAndCat)
    tests["hashtagCategories"] = hashtags
    return tests

def currentDateString():
    """Retrieves the current date string.

    Returns:
        String -- Current date and time.
    """
    
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")

def generateGroundTruth(formattedTests, provider, testRun=False):
    """Uses generated hashtags and a level 0 category to find news articles through Google News, extracts their text and stores the data in a local Mongo DB.

    Arguments:
        formattedTests {Dictionary} -- level 0 categories and formatted hashtags
        provider {String} -- Provider name, either 'Google' or 'Ibm'

    Keyword Arguments:
        testRun {bool} -- Does not store to MongoDB if set to True (default: {False})
    """
    
    succeededTotal = 0
    failedTotal = 0
    duplicatesTotal = 0
    
    progress = 1
    for tagAndCat in formattedTests["hashtagCategories"]:
        hashtag = tagAndCat['hashtag']
        l1PlusCat = tagAndCat['category']
        
        print("... "+provider+" ... Searching for hashtag: "+hashtag+" ("+str(progress)+"/"+str(len(formattedTests["hashtagCategories"]))+") with testCategory: "+formattedTests["testCategory"]+" ...")
        progress += 1
        tweets = TwitterSearch.getData(hashtag) # e.g. ['', 'https://www.bloomberg.com/news/articles/2020-03-08/apple-s-...', ['Apple', 'Coronavid19']]
        print("... found "+str(len(tweets))+" tweets ...")
        for tweet in tweets: # get the article for the tweets external URL for each retrieved tweet and append all data as dictionary to gGoundTruthData
            articleData = TwitterNewsReader.readArticle(tweet[1]) # get article data
            
            tweetHashtags = "" # stringify all hashtags of the found tweet
            for i in range(len(tweet[2])):
                if i != len(tweet[2])-1:
                    tweetHashtags += tweet[2][i]+", "
                else:
                    tweetHashtags += tweet[2][i]
                    
            if (articleData["site_article"] == "" or articleData["site_title"] == ""):
                failedTotal += 1
                continue # Could not fetch article -> continue with other tweets
            
            collection = googleGroundTruth
            if provider == "Ibm":
                collection = ibmGroundTruth
                
            collectionTC = googleGroundTruthTC
            if provider == "Ibm":
                collectionTC = ibmGroundTruthTC
            
            if collection.count_documents({"article_hash" : hashlib.md5(articleData["site_article"].encode('utf-8')).hexdigest()}) != 0: # check if article already exists
                duplicatesTotal += 1
                continue
            
            if not testRun:              
                collection.insert_one({
                    "provider" : provider,
                    "test_date" : currentDateString(),
                    "article_hash" : hashlib.md5(articleData["site_article"].encode('utf-8')).hexdigest(),
                    "test_category" : formattedTests["testCategory"],
                    "search_hashtag" : hashtag,
                    "search_category" : l1PlusCat,
                    "tweet" : {
                        "hashtags" : tweetHashtags,
                        "external_url" : tweet[1]
                    },
                    "article" : articleData,
                    "article_meta" : {
                        "character_count" : str(len(articleData["site_article"]))
                    }
                })
                
                collectionTC.insert_one({
                    "test_category": formattedTests["testCategory"],
                    "test_date" : currentDateString()
                })
            
            succeededTotal += 1
            
    print("succeededTotal: " + str(succeededTotal))
    print("failedTotal: " + str(failedTotal))
    print("duplicatesTotal: " + str(duplicatesTotal))
        

#   1) searches for suitable l1 -> l0 tests
#   2) pre-processes the category names (remove: blank spaces, words in brackets, non alpha characters, and more)
#   3) find up to 30 tweets (defined in readArticle.py) with external URLs to news articles using the pre-processed category names
#   4) retrieve and parse the news article's texts and store everything in a dictionary

# Usage Example:

#while 1:
#    sleepTime = randrange(300, 900) # sleep 5 to 15 minutes
#    generateGroundTruth(generateHashtags(getRandomTests("Google")), "Google", testRun=False)
#    print("... sleeping " + str(sleepTime) + " seconds ...")
#    time.sleep(sleepTime)
#    sleepTime = randrange(300, 900) # sleep 5 to 15 minutes
#    generateGroundTruth(generateHashtags(getRandomTests("Ibm")), "Ibm", testRun=False)
#    print("... sleeping " + str(sleepTime) + " seconds ...")
#    time.sleep(sleepTime)

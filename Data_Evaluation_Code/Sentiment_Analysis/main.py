import sys
sys.path.append('../')
sys.path.append('../..')
from datetime import datetime
import enum

import numpy as np
from nltk import word_tokenize, sent_tokenize, pos_tag
import psutil

from mongo_connect import Connect
import sentiment_analysis_calls as ServiceCalls
import coReferences
import negations
import unknown_words

### Mongo DB Init ###
connection = Connect.get_connection()
db = connection.sentimentAnalysis
allYelpReviews = db.allYelpReviews
evaluationResults = db.evaluationResults
###               ###


class PolarityOffset:
    """
    A class containing the polarity offsets of the four providers.
    """
    def __init__(self, ibm, google, microsoft, amazon):
        self.ibm = ibm
        self.google = google
        self.microsoft = microsoft
        self.amazon = amazon


class TimeForCompletion:
    """
    A class containing the time for completion of the four providers.
    """
    def __init__(self, ibm, google, microsoft, amazon):
        self.ibm = ibm
        self.google = google
        self.microsoft = microsoft
        self.amazon = amazon


class ErrorMessage:
    """
    A class containing the error messages of the four providers.
    """
    def __init__(self, ibm, google, microsoft, amazon):
        self.ibm = ibm
        self.google = google
        self.microsoft = microsoft
        self.amazon = amazon


class YelpReview:
    """
    A class consiting of a Yelp Reviews attributes.
    """
    def __init__(self, reviewId, stars, text, usefulness, reviewDate):
        self.reviewId = reviewId
        self.stars = stars
        self.text = text
        self.usefulness = usefulness
        self.characterCount = len(text)
        self.reviewDate = reviewDate


class SentimentTest:
    completed = False

    def __init__(self, minUsefulness=None,
                 maxUsefulness=None,
                 minTextLength=None,
                 maxTextLength=None,
                 minStars=None,
                 maxStars=None,
                 polarityOffeset=None,
                 timeForCompletion=None,
                 yelpReview=None,
                 errorMessage=None):
        self.minUsefulness = minUsefulness
        self.maxUsefulness = maxUsefulness
        self.minTextLength = minTextLength
        self.maxTextLength = maxTextLength
        self.minStars = minStars
        self.maxStars = maxStars
        self.polarityOffeset = polarityOffeset
        self.timeForCompletion = timeForCompletion
        self.yelpReview = yelpReview
        self.errorMessage = errorMessage

    def setPolarityOffset(self, offset):
        self.polarityOffeset = offset

    def setTimeForCompletion(self, time):
        self.timeForCompletion = time

    def setYelpReview(self, review):
        self.yelpReview = review

    def setErrorMessave(self, message):
        self.errorMessage = message

    def completedTest(self):
        self.completed = True

    def matchesSettings(self, review: YelpReview):
        if self.minUsefulness == review.usefulness:
            return True

    def __str__(self):
        return "usefulness: "+str(self.minUsefulness)+"-"+str(self.maxUsefulness)+", textLength: "+str(self.minTextLength)+"-"+str(self.maxTextLength)+", stars: "+str(self.minStars)+"-"+str(self.maxStars)


class DegradingUsefulness(SentimentTest):
    def __str__(self):
        return super(DegradingUsefulness, self).__str__()


class DegradingTextLength(SentimentTest):
    def __str__(self):
        return super(DegradingTextLength, self).__str__()


class DegradingStarCount(SentimentTest):

    def __str__(self):
        return super(DegradingStarCount, self).__str__()


class SentimentTests(object):
    class Type(enum.IntEnum):
        DEGRADING_USEFULNESS = 0 # usefulness degrades in three stages, other parameters 'optimal'
        DEGRADING_TEXT_LENGTH = 1 # text length degrades in three stages, other parameters 'optimal'
        DEGRADING_STAR_COUNT = 2 # star count degrades in three stages, other parameters 'optimal'
        SET_USEFULNESS = 3 # set text usefulness (1 to 10), other parameters random
        SET_TEXT_LENGTH = 4 # set text length (50 to 1000), other parameters random
        SET_STAR_COUNT = 5 # set star number (1 to 5), other parameters random


def buildTests(nOfTests, testType, textLength=None, starCount=None, usefulness=None):
    tests = []
    testSizes = np.array_split(range(nOfTests), 3)
    if testType == SentimentTests.Type.DEGRADING_TEXT_LENGTH:
        for _ in testSizes[0]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=500, maxTextLength=1000, minStars=2, maxStars=4))
        for _ in testSizes[1]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=150, maxTextLength=499, minStars=2, maxStars=4))
        for _ in testSizes[2]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=50, maxTextLength=149, minStars=2, maxStars=4))
    if testType == SentimentTests.Type.DEGRADING_STAR_COUNT:
        for _ in testSizes[0]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=150, maxTextLength=499, minStars=1, maxStars=1))
        for _ in testSizes[1]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=150, maxTextLength=499, minStars=2, maxStars=4))
        for _ in testSizes[2]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=150, maxTextLength=499, minStars=5, maxStars=5))
    if testType == SentimentTests.Type.DEGRADING_USEFULNESS:
        for _ in testSizes[0]:
            tests.append(DegradingUsefulness(minUsefulness=8, maxUsefulness=10,
                                             minTextLength=150, maxTextLength=499, minStars=2, maxStars=4))
        for _ in testSizes[1]:
            tests.append(DegradingUsefulness(minUsefulness=5, maxUsefulness=7,
                                             minTextLength=150, maxTextLength=499, minStars=2, maxStars=4))
        for _ in testSizes[2]:
            tests.append(DegradingUsefulness(minUsefulness=1, maxUsefulness=4,
                                             minTextLength=150, maxTextLength=499, minStars=2, maxStars=4))
    if testType == SentimentTests.Type.SET_TEXT_LENGTH:
        for _ in range(nOfTests):
            tests.append(DegradingUsefulness(minUsefulness=1, maxUsefulness=10,
                                             minTextLength=textLength, maxTextLength=textLength, minStars=1, maxStars=5))
    if testType == SentimentTests.Type.SET_STAR_COUNT:
        for _ in range(nOfTests):
            tests.append(DegradingUsefulness(minUsefulness=1, maxUsefulness=10,
                                             minTextLength=50, maxTextLength=1000, minStars=starCount, maxStars=starCount))
    if testType == SentimentTests.Type.SET_USEFULNESS:
        for _ in range(nOfTests):
            tests.append(DegradingUsefulness(minUsefulness=usefulness, maxUsefulness=usefulness,
                                             minTextLength=50, maxTextLength=1000, minStars=1, maxStars=5))
        

    return tests


def runTest(test):
    print("Running test "+str(test.yelpReview.reviewId)+" ...")
    result = ServiceCalls.makeCalls(
        text=test.yelpReview.text, stars=test.yelpReview.stars)
    test.setPolarityOffset(PolarityOffset(ibm=result['values']['ibm']['polarity_offsets'],
                                          google=result['values']['google']['polarity_offsets'],
                                          microsoft=result['values']['microsoft']['polarity_offsets'],
                                          amazon=result['values']['amazon']['polarity_offsets']))
    test.setTimeForCompletion(TimeForCompletion(ibm=result['values']['ibm']['time_for_completion'],
                                                google=result['values']['google']['time_for_completion'],
                                                microsoft=result['values']['microsoft']['time_for_completion'],
                                                amazon=result['values']['amazon']['time_for_completion']))
    test.setErrorMessave(ErrorMessage(ibm=result['errors']['ibm'],
                                      google=result['errors']['google'],
                                      microsoft=result['errors']['microsoft'],
                                      amazon=result['errors']['amazon']))
    print("Test done")
    return test


def getParseReviews(tests: [SentimentTest]):
    """
    Retrieves a previously unprocessed Yelp Review from a local Mongo DB database and parses it. The types of testes (min/max stars, usefulness, and textLength) is determined by the passed in list of SentimentTest.

    Arguments:
        tests {List} -- A list of sentiment tests
    """
    
    count = 1
    failedCount = 0
    for test in tests:
        print("Test "+str(count)+"/"+str(len(tests)))
        print("Failed operations so far: "+str(failedCount))
        print("Querying dataset for a review: "+str(test))
        pipeline = [
            # Due to PERFORMANCE ISSUES we rather duplicate the entire groundTruth dataset and then delete the used entries, rather than checking if we previously used them before
            
            #{"$lookup": {"from": "evaluationResults", "localField": "review_id",
            #             "foreignField": "test_id", "as": "toMatch"}},
            # do not include previously used reviews
            #{"$match": {"toMatch": {"$eq": []}}},
            
            {"$match": {"usefulness": {"$gte": test.minUsefulness}}},
            {"$match": {"usefulness": {"$lte": test.maxUsefulness}}},
            {"$match": {"characterCount": {"$gte": test.minTextLength}}},
            {"$match": {"characterCount": {"$lte": test.maxTextLength}}},
            {"$match": {"stars": {"$gte": test.minStars}}},
            {"$match": {"stars": {"$lte": test.maxStars}}},
            {"$sample": {"size": 1}}
        ]

        reviews = list(allYelpReviews.aggregate(pipeline))
        if len(reviews) >= 1:
            review = reviews[0]
            test.setYelpReview(YelpReview(
                reviewId=review['review_id'], stars=review['stars'], text=review['text'], usefulness=review['usefulness'], reviewDate=review['reviewDate']))
            print("Found review "+str(review['review_id']))
            allYelpReviews.delete_one({"review_id" : review["review_id"]}) # for performance (see explanation above)
            print("Deleted review "+str(review['review_id']))
            count += 1
            testResult = makeResult(test)
            if(testResult.polarityOffeset.ibm < -5 or testResult.polarityOffeset.google < -5 or testResult.polarityOffeset.microsoft < -5 or testResult.polarityOffeset.amazon < -5): # Something went wrong (usually the maximal amount of requests per time reached)
                failedCount += 1
                #os.system('say "Error"') # just for fun
        else:
            print("No reviews found for the provided criteria.")
            continue


def wordCount(text):
    """
    Counts the number of words in a text string using the NLTK word_tokenize() function.

    Arguments:
        text {String} -- The text to be analyzed

    Returns:
        Integer -- The number of words
    """
    count = 0
    wds = word_tokenize(text)
    for wd in wds:
        if len(wd) > 1:
            count += 1
    return count


def verbs(text): # also counts and lists multiple occurrences
    """
    Counts the number of verbs in a text string using the NLTK pos_tag() and word_tokenize() function.

    Arguments:
        text {String} -- The text to be analyzed

    Returns:
        Dictionary -- The number of verbs and their values
    """
    count = 0
    words = ""
    for wd, pos in pos_tag(word_tokenize(text)):
        if pos.startswith('VB'):  # VB (base form), VBD (past tense), VBG (gerund/present particile), VBN (past participle), VBP (sing. present), VBZ (3rd person sing. present)
            count += 1
            words += wd+", "
    if len(words) >= 2:
        words = words[:-2] # remove ", " at the end
    return {"count": count,
            "words": words}


def nouns(text): # also counts and lists multiple occurrences
    """
    Counts the number of nouns in a text string using the NLTK pos_tag() and word_tokenize() function.

    Arguments:
        text {String} -- The text to be analyzed

    Returns:
        Dictionary -- The number of nouns and their values
    """
    count = 0
    words = ""
    for wd, pos in pos_tag(word_tokenize(text)):
        # NN (noun singular), NNS (noun plural), NNP (proper noun singular), NNPS (proper noun plural)
        if pos.startswith('NN'):
            count += 1
            words += wd+", "
    if len(words) >= 2:
        words = words[:-2] # remove ", " at the end
    return {"count": count,
            "words": words}


def adjs(text): # also counts and lists multiple occurrences
    """
    Counts the number of adjectives in a text string using the NLTK pos_tag() and word_tokenize() function.

    Arguments:
        text {String} -- The text to be analyzed

    Returns:
        Dictionary -- The number of adjectives and their values
    """
    count = 0
    words = ""
    for wd, pos in pos_tag(word_tokenize(text)):
        if pos.startswith('JJ'):  # JJ (adjective), JJR (comparative), JJS (superlative)
            count += 1
            words += wd+", "
    if len(words) >= 2:
        words = words[:-2] # remove ", " at the end
    return {"count": count,
            "words": words}


def condWords(text): # also counts and lists multiple occurrences
    """
    Counts the number of conditional words (prepositions/subordinating conjunctions) in a text string using the NLTK pos_tag() and word_tokenize() function.

    Arguments:
        text {String} -- The text to be analyzed

    Returns:
        Dictionary -- The number of conditional words and their values
    """
    count = 0
    words = ""
    for wd, pos in pos_tag(word_tokenize(text)):
        if pos.startswith('IN'):  # IN preposition/subordinating conjunction
            count += 1
            words += wd+", "
    if(len(words) >= 2): words = words[:-2] # remove ", " at the end
    return {"count": count,
            "words": words}


def currentDateString():
    """
    Returns the current date and time.

    Returns:
        String -- The current date and time
    """
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def makeResult(test):
    testResult = runTest(test)
    storeResult(testResult)
    return testResult


def storeResult(testResult):
    """
    This function stores the sentiment analysis evaluation results in a local Mongo DB database.

    Arguments:
        testResult {Dictionary} -- A dictionary of a test's results
    """
    
    print("Storing results ...")
    if(testResult.polarityOffeset.ibm < -5 or testResult.polarityOffeset.google < -5 or testResult.polarityOffeset.microsoft < -5 or testResult.polarityOffeset.amazon < -5):
        print("Round failed.")
        # Failed -> Most of the time because of expired AWS credentials or exceeded rate limits
    else:
        # all NLP calls were OK
        evaluationResults.insert_one(
            {"test_id": testResult.yelpReview.reviewId,
             "test_date": currentDateString(),
             "polarity_offsets": {"val": {"ibm": testResult.polarityOffeset.ibm,
                                          "google": testResult.polarityOffeset.google,
                                          "microsoft": testResult.polarityOffeset.microsoft,
                                          "amazon": testResult.polarityOffeset.amazon},
                                  "abs_val": {"ibm": abs(testResult.polarityOffeset.ibm),
                                              "google": abs(testResult.polarityOffeset.google),
                                              "microsoft": abs(testResult.polarityOffeset.microsoft),
                                              "amazon": abs(testResult.polarityOffeset.amazon)}},
             "time_for_completion": {"ibm": testResult.timeForCompletion.ibm,
                                     "google": testResult.timeForCompletion.google,
                                     "microsoft": testResult.timeForCompletion.microsoft,
                                     "amazon": testResult.timeForCompletion.amazon},
             "yelp_review": {"review_id": testResult.yelpReview.reviewId,
                             "review_date": testResult.yelpReview.reviewDate,
                             "text": testResult.yelpReview.text,
                             "stars": testResult.yelpReview.stars,
                             "usefulness": testResult.yelpReview.usefulness,
                             "unknown_words": unknown_words.measureUnknownWords(testResult.yelpReview.text),
                             "pos_verbs": {"count": verbs(testResult.yelpReview.text)['count'],
                                           "values": verbs(testResult.yelpReview.text)['words'],
                                           "percentage": round(verbs(testResult.yelpReview.text)['count']/wordCount(testResult.yelpReview.text),2)},
                             "pos_nouns": {"count": nouns(testResult.yelpReview.text)['count'],
                                                "values": nouns(testResult.yelpReview.text)['words'],
                                                "percentage": round(nouns(testResult.yelpReview.text)['count']/wordCount(testResult.yelpReview.text),2)},
                             "pos_adjs": {"count": adjs(testResult.yelpReview.text)['count'],
                                               "values": adjs(testResult.yelpReview.text)['words'],
                                               "percentage": round(adjs(testResult.yelpReview.text)['count']/wordCount(testResult.yelpReview.text),2)},
                             "cond_words": {"count": condWords(testResult.yelpReview.text)['count'],
                                               "values": condWords(testResult.yelpReview.text)['words'],
                                               "percentage": round(condWords(testResult.yelpReview.text)['count']/wordCount(testResult.yelpReview.text),2)},
                             "coRefs": coReferences.coRefs(testResult.yelpReview.text),
                             "negations": negations.measureNegations(testResult.yelpReview.text),
                             "commas": {"count": testResult.yelpReview.text.count(","),
                                             "percentage": round(testResult.yelpReview.text.count(",")/wordCount(testResult.yelpReview.text),2)},
                             "character_count": testResult.yelpReview.characterCount,
                             "word_count": wordCount(testResult.yelpReview.text),
                             "sentence_count": len(sent_tokenize(testResult.yelpReview.text))},
             "runtime_Env": {"python_version": "Python 3.7.5 64-bit",
                             "machine_info": "MacBookPro16,1 | 2,3 GHz 8-Core Intel Core i9 | 64 GB 2667 MHz DDR4",
                             "available_ram": str(round(psutil.virtual_memory().available/float(1 << 20)))+" MB / 65536 MB",
                             "internet_router": "Vodafone Docsis 3.1 | 01.01.117.01.EURO",
                             "internet_speed": "Down: 100 Mbit/s | Up: 50 Mbit/s",
                             "internet_connection_type": "Wi-Fi",
                             "geo_location": "Berlin, Germany",
                             "parallel_requests": "false"},
             "failed": 0,
             "nlp_library_versions": {"ibm": "ibm-cloud-sdk-core-1.5.1 ibm-watson-4.3.0",
                                      "google": "google-api-core-1.15.0 google-cloud-language-1.3.0",
                                      "microsoft": "azure-core-1.2.2 azure-ai-textanalytics-1.0.0b2",
                                      "amazon": "awscli-1.18.5 boto3-1.12.5"}
             })

    print("Stored results "+str(testResult.yelpReview.reviewId))


def startTests(nOfTests, testType, textLength=0, starCount=0, usefulness=0):
    """
    The function allows the operator the retrieve and evaluate specific types of Yelp Reviews, depending on the textLength, starCount, and usefulness values. We therefore provide a numnber of test presets and also allow one the values to be set indidually.

    Arguments:
        nOfTests {Integer} -- The number of Yelp Reviews to retrieve and evaluate
        testType {SentimentTest} -- One of 6 possible test types

    Keyword Arguments:
        textLength {int} -- Set the exact text length, a Yelp Review should have (default: {0})
        starCount {int} -- Set the exact star count, a Yelp Review should have (default: {0})
        usefulness {int} -- Set the exact usefulness, a Yelp Review should have (default: {0})

    Raises:
        ValueError: textLength must be an Integer between 50 and 1000
        ValueError: starCount must be an Integer between 1 and 5
        ValueError: usefulness must be an Integer between 1 and 10
    """
    if testType == SentimentTests.Type.SET_TEXT_LENGTH and (not 50 <= textLength <= 1000 or not isinstance(textLength, int)):
        raise ValueError("textLength must be an Integer between 50 and 1000")
    if testType == SentimentTests.Type.SET_STAR_COUNT and (not 1 <= starCount <= 5 or not isinstance(starCount, int)):
        raise ValueError("starCount must be an Integer between 1 and 5")
    if testType == SentimentTests.Type.SET_USEFULNESS and (not 1 <= usefulness <= 10 or not isinstance(textLength, int)):
        raise ValueError("usefulness must be an Integer between 1 and 10")
    getParseReviews(buildTests(nOfTests, testType, textLength=textLength, starCount=starCount, usefulness=usefulness))



# Usage Example:

#startTests(300, SentimentTests.Type.DEGRADING_TEXT_LENGTH)
#startTests(300, SentimentTests.Type.DEGRADING_STAR_COUNT)
#startTests(300, SentimentTests.Type.DEGRADING_USEFULNESS)

#startTests(50, SentimentTests.Type.SET_TEXT_LENGTH, textLength=200)
#startTests(50, SentimentTests.Type.SET_STAR_COUNT, starCount=3)
#startTests(50, SentimentTests.Type.SET_USEFULNESS, usefulness=10)

import sys
sys.path.append('../')
sys.path.append('../..')
from datetime import datetime
from nltk import word_tokenize, pos_tag
import psutil
import unknown_words
import content_classification_calls as ServiceCalls
from mongo_connect import Connect

### Mongo DB Init ###
connection = Connect.get_connection()

db = connection.contentClassification

googleGroundTruthCopy = db.googleGroundTruthCopy  # only work on copy
ibmGroundTruthCopy = db.ibmGroundTruthCopy  # only work on copy
evaluationResultsGoogle = db.evaluationResultsGoogle
evaluationResultsIBM = db.evaluationResultsIBM
###               ###


def currentDateString():
    """
    Gets the current date and time as string.

    Returns:
        String -- The current date and time
    """
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


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


def nouns(text):  # also counts and lists multiple occurrences
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
        words = words[:-2]  # remove ", " at the end
    return {"count": count,
            "words": words}


def googleGetTest():
    """
    Retrieves one Google CC test sentence from a local MongoDB database.

    Returns:
        Dictionary -- An annotated test sentence
    """
    test = googleGroundTruthCopy.find_one()
    return test


def ibmGetTest():
    """
    Retrieves one IBM CC test sentence from a local MongoDB database.

    Returns:
        Dictionary -- An annotated test sentence
    """
    test = ibmGroundTruthCopy.find_one()
    return test


def googleTestOne():
    """
    Performs all the necessary calls the retrieve, evaluate, and store a content classification test news article for Google's service.

    Returns:
        Integer -- Returns 1 if the to be evaluated text was to short (under 20 words), and 0 otherwise
    """
    print("Getting Google test ...")
    test = googleGetTest()
    testCategory = test['test_category']  # l0
    searchCategory = test['search_category']  # l1+
    articleText = test['article']['site_article']
    if wordCount(articleText) < 20:
        print("Article text to short. Skipping...")
        googleGroundTruthCopy.delete_one({"_id": test["_id"]})
        return 1
    print("Testing ...")
    testResult = ServiceCalls.googleMakeCall(articleText)

    l0Detected = 0
    l1pDetected = 0
    for detectedCategory in testResult['categories']:
        if testCategory in detectedCategory['category']:
            l0Detected = 1
        if searchCategory in detectedCategory['category']:
            l1pDetected = 1

    print("Storing ...")
    evaluationResultsGoogle.insert_one({
        "test_id": test['article_hash'],
        "test_date": currentDateString(),
        "result": {
            "l0_detected": l0Detected,
            "l1p_detected": l1pDetected
        },
        "provider_response": testResult,
        "article": {
            "article_hash": test['article_hash'],
            "retrieval_date": test['test_date'],
            "test_category": testCategory,
            "search_category": searchCategory,
            "unknown_words": unknown_words.measureUnknownWords(articleText),
            "pos_nouns": {"count": nouns(articleText)['count'],
                          "values": nouns(articleText)['words'],
                          "percentage": round(nouns(articleText)['count']/wordCount(articleText), 2)},
            "word_count": wordCount(articleText)
        },
        "runtime_Env": {"python_version": "Python 3.7.5 64-bit",
                        "machine_info": "MacBookPro16,1 | 2,3 GHz 8-Core Intel Core i9 | 64 GB 2667 MHz DDR4",
                        "available_ram": str(round(psutil.virtual_memory().available/float(1 << 20)))+" MB / 65536 MB",
                        "internet_router": "Vodafone Docsis 3.1 | 01.01.117.01.EURO",
                        "internet_speed": "Down: 100 Mbit/s | Up: 50 Mbit/s",
                        "internet_connection_type": "Wi-Fi",
                        "geo_location": "Berlin, Germany",
                        "parallel_requests": "false"},
        "failed": int(len(testResult['categories']) == 0),
        "nlp_library_versions": {"ibm": "ibm-cloud-sdk-core-1.5.1 ibm-watson-4.3.0",
                                 "google": "google-api-core-1.15.0 google-cloud-language-1.3.0",
                                 "microsoft": "azure-core-1.2.2 azure-ai-textanalytics-1.0.0b2",
                                 "amazon": "awscli-1.18.5 boto3-1.12.5"}
    })
    print("Deleting test from copy ...")
    googleGroundTruthCopy.delete_one({"_id": test["_id"]})
    print("Done.")
    return 0


def ibmTestOne():
    """
    Performs all the necessary calls the retrieve, evaluate, and store a content classification test news article for IBM's service.

    Returns:
        Integer -- Returns 1 if the to be evaluated text was to short (under 20 words), and 0 otherwise
    """
    print("Getting IBM test ...")
    test = ibmGetTest()
    testCategory = test['test_category']  # l0
    searchCategory = test['search_category']  # l1+
    articleText = test['article']['site_article']
    if wordCount(articleText) < 20:
        print("Article text to short. Skipping...")
        ibmGroundTruthCopy.delete_one({"_id": test["_id"]})
        return 1
    print("Testing ...")
    testResult = ServiceCalls.ibmMakeCall(articleText)

    l0Detected = 0
    l1pDetected = 0
    for detectedCategory in testResult['categories']:
        if testCategory in detectedCategory['category']:
            l0Detected = 1
        if searchCategory in detectedCategory['category']:
            l1pDetected = 1

    print("Storing ...")
    evaluationResultsIBM.insert_one({
        "test_id": test['article_hash'],
        "test_date": currentDateString(),
        "result": {
            "l0_detected": l0Detected,
            "l1p_detected": l1pDetected
        },
        "provider_response": testResult,
        "article": {
            "article_hash": test['article_hash'],
            "retrieval_date": test['test_date'],
            "test_category": testCategory,
            "search_category": searchCategory,
            "unknown_words": unknown_words.measureUnknownWords(articleText),
            "pos_nouns": {"count": nouns(articleText)['count'],
                          "values": nouns(articleText)['words'],
                          "percentage": round(nouns(articleText)['count']/wordCount(articleText), 2)},
            "word_count": wordCount(articleText)
        },
        "runtime_Env": {"python_version": "Python 3.7.5 64-bit",
                        "machine_info": "MacBookPro16,1 | 2,3 GHz 8-Core Intel Core i9 | 64 GB 2667 MHz DDR4",
                        "available_ram": str(round(psutil.virtual_memory().available/float(1 << 20)))+" MB / 65536 MB",
                        "internet_router": "Vodafone Docsis 3.1 | 01.01.117.01.EURO",
                        "internet_speed": "Down: 100 Mbit/s | Up: 50 Mbit/s",
                        "internet_connection_type": "Wi-Fi",
                        "geo_location": "Berlin, Germany",
                        "parallel_requests": "false"},
        "failed": int(len(testResult['categories']) == 0),
        "nlp_library_versions": {"ibm": "ibm-cloud-sdk-core-1.5.1 ibm-watson-4.3.0",
                                 "google": "google-api-core-1.15.0 google-cloud-language-1.3.0",
                                 "microsoft": "azure-core-1.2.2 azure-ai-textanalytics-1.0.0b2",
                                 "amazon": "awscli-1.18.5 boto3-1.12.5"}
    })
    print("Deleting test from copy ...")
    ibmGroundTruthCopy.delete_one({"_id": test["_id"]})
    print("Done.")
    return 0


# Usage Example:

#while 1:
#    googleTestOne()
#    ibmTestOne()

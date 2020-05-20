import sys
sys.path.append('../')
sys.path.append('../..')
from datetime import datetime
import psutil
from mongo_connect import Connect
import syntax_analysis_calls as ServiceCalls

### Mongo DB Init ###
connection = Connect.get_connection()

db = connection.syntaxAnalysis

udGroundTruthCopy = db.udGroundTruthCopy  # only work on copy
udPTGroundTruthCopy = db.udPTGroundTruthCopy  # only work on copy
udEWGroundTruthCopy = db.udEWGroundTruthCopy  # only work on copy
nvGroundTruthCopy = db.nvGroundTruthCopy  # only work on copy

udEvaluationResults = db.udEvaluationResults
udPTEvaluationResults = db.udPTEvaluationResults
udEWEvaluationResults = db.udEWEvaluationResults
nvEvaluationResults = db.nvEvaluationResults
###               ###


def currentDateString():
    """
    Gets the current date and time as string.

    Returns:
        String -- The current date and time
    """
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def udGetTest():
    """
    Retrieves one UD (GUM) test sentence from a local MongoDB database.

    Returns:
        Dictionary -- An annotated test sentence
    """
    test = udGroundTruthCopy.find_one()
    return test


def udPTGetTest():
    """
    Retrieves one UD (PT) test sentence from a local MongoDB database.

    Returns:
        Dictionary -- An annotated test sentence
    """
    test = udPTGroundTruthCopy.find_one()
    return test


def udEWGetTest():
    """
    Retrieves one UD (EW) test sentence from a local MongoDB database.

    Returns:
        Dictionary -- An annotated test sentence
    """
    test = udEWGroundTruthCopy.find_one()
    return test


def nvGetTest():
    """
    Retrieves one Noun Verb test sentence from a local MongoDB database.

    Returns:
        Dictionary -- An annotated test sentence
    """
    test = nvGroundTruthCopy.find_one()
    return test


def evaluateUD(tokensArrayGT, tokensArrayProvider):
    """Measures the number of tagged and the number of correctly tagged tokens per sentence for one provider. For reasons of simplicity, we do not care about the token offset, i.e. if a word occured twice, one as e.g. noun
    and once as e.g. verb, but in the wrong sequence, the system would still count this as correct. We therefore also have a seperate Noun-Verb ambigiuity test.

    Arguments:
        tokensArrayGT {List} -- List of ground-truth POS tokens
        tokensArrayProvider {List} -- List of provider POS tokens to be tested

    Returns:
        Dictionary -- The number of ground-truth tokens and provider tokens (to calculate recall) and the number of correct provider tokens (to calculate precision)
    """
    
    gtTokenCount = len(tokensArrayGT)
    providerTokenCount = len(tokensArrayProvider)
    providerTokenCorrectCount = 0
    for tokenGT in tokensArrayGT:
        tokenText = tokenGT['token_text']
        #tokenBeginOffset = tokenGT['token_begin_offset']
        posTag = tokenGT['pos_tag']
        for tokenProvider in tokensArrayProvider:
            # if tokenProvider['token_text'] == tokenText and tokenProvider['token_begin_offset'] == tokenBeginOffset:
            #    if tokenProvider['pos_tag'] == posTag:
            #        providerTokenCorrectCount += 1
            #        break
            # this ignores noun-verb ambiguities
            if tokenProvider['token_text'] == tokenText and tokenProvider['pos_tag'] == posTag:
                providerTokenCorrectCount += 1
                break
    if providerTokenCorrectCount > providerTokenCount or providerTokenCorrectCount > gtTokenCount:
        print("Error evaluateUD")
        print(tokensArrayGT)
        return {}
    return({
        "gt_Tokens": gtTokenCount,
        "provider_Tokens": providerTokenCount,
        "provider_Tokens_Correct": providerTokenCorrectCount
    })


def evaluateUDGoogleSpecial(tokensArrayGT, tokensArrayProvider):
    """See evaluateUD, except we account for Google's service not being able to recognize the POS tags 'INTJ', 'SCONJ', and 'SYM'. The total count of ground-truth tokens is deducted by the occurence count of these three tags.

    Arguments:
        tokensArrayGT {List} -- List of ground-truth POS tokens
        tokensArrayProvider {List} -- List of provider POS tokens to be tested

    Returns:
        Dictionary -- The number of ground-truth tokens and provider tokens (to calculate recall) and the number of correct provider tokens (to calculate precision)
    """
    
    gtTokenCount = 0  # dif
    for tokenGTfc in tokensArrayGT:  # dif
        if not tokenGTfc['pos_tag'] == 'INTJ' and not tokenGTfc['pos_tag'] == 'SCONJ' and not tokenGTfc['pos_tag'] == 'SYM':  # dif
            gtTokenCount += 1  # dif

    providerTokenCount = len(tokensArrayProvider)
    providerTokenCorrectCount = 0
    for tokenGT in tokensArrayGT:
        tokenText = tokenGT['token_text']
        #tokenBeginOffset = tokenGT['token_begin_offset']
        posTag = tokenGT['pos_tag']
        for tokenProvider in tokensArrayProvider:
            # if tokenProvider['token_text'] == tokenText and tokenProvider['token_begin_offset'] == tokenBeginOffset:
            #    if tokenProvider['pos_tag'] == posTag:
            #        providerTokenCorrectCount += 1
            #        break
            # this ignores noun-verb ambiguities
            if tokenProvider['token_text'] == tokenText and tokenProvider['pos_tag'] == posTag:
                providerTokenCorrectCount += 1
                break
    if providerTokenCorrectCount > len(tokensArrayProvider) or providerTokenCorrectCount > len(tokensArrayGT):  # dif
        print("Error evaluateUD GoogleSpecial")
        print(tokensArrayGT)
        return {}
    return({
        "gt_Tokens": gtTokenCount,
        "provider_Tokens": providerTokenCount,
        "provider_Tokens_Correct": providerTokenCorrectCount
    })


def evaluateNV(tokenTextGT, tokenPOSGT, tokensArrayProvider):
    """Returns 1 if the provider correctly annotated a VERB as VERB, or if the provider correctly annotated a NON-VERB as anything other than VERB. In all other cases it returns 0.

    Arguments:
        tokenTextGT {String} -- Token text, e.g. 'star'
        tokenPOSGT {String} -- Token POS, 'VERB' or 'NON-VERB'
        tokensArrayProvider {List} -- List of provider POS tokens to be tested

    Returns:
        Integer -- 1 for correct, 0 for incorrect
    """
    
    if tokenPOSGT == "VERB":
        for tokenProvider in tokensArrayProvider:
            if tokenProvider['token_text'] == tokenTextGT and tokenProvider['pos_tag'] == "VERB":
                return 1  # correct
            elif tokenProvider['token_text'] == tokenTextGT and not tokenProvider['pos_tag'] == "VERB":
                return 0  # incorrect
    else:
        for tokenProvider in tokensArrayProvider:
            if tokenProvider['token_text'] == tokenTextGT and not tokenProvider['pos_tag'] == "VERB":
                return 1  # correct
            elif tokenProvider['token_text'] == tokenTextGT and tokenProvider['pos_tag'] == "VERB":
                return 0  # incorrect
    return 0  # default


def udTestOne(test, sourceDb, resultDb):
    """Performs all the calls to evaluate a provider's response to a UD (3 types) test sentence and retores all results in a local MongoDB database.

    Arguments:
        test {Dictionary} -- A annotated test document from a local MongoDB for testing
        sourceDb {Collection} -- The source (GET) DB collection
        resultDb {Collection} -- The result (POST) DB collection
    """
    
    testSentence = test['sentence']
    tokens = test['annotation']

    print("Testing ...")
    testResult = ServiceCalls.makeCalls(testSentence)

    failed = 0
    if len(testResult['values']['ibm']['tokens']) == 0:
        failed = 1
    if len(testResult['values']['google']['tokens']) == 0:
        failed = 1
    if len(testResult['values']['amazon']['tokens']) == 0:
        failed = 1

    ibmEvaluation = {}
    googleEvaluation = {}
    amazonEvaluation = {}
    googleEvaluationSpecial = {}

    if failed == 0:
        ibmEvaluation = evaluateUD(
            tokens, testResult['values']['ibm']['tokens'])
        googleEvaluation = evaluateUD(
            tokens, testResult['values']['google']['tokens'])
        googleEvaluationSpecial = evaluateUDGoogleSpecial(
            tokens, testResult['values']['google']['tokens'])
        amazonEvaluation = evaluateUD(
            tokens, testResult['values']['amazon']['tokens'])

    if not ibmEvaluation or not googleEvaluation or not googleEvaluationSpecial or not amazonEvaluation:
        print("Not Storing ...")
        sourceDb.delete_one({"_id": test["_id"]})
        return

    print("Storing ...")
    resultDb.insert_one({
        "test_id": test['_id'],
        "test_date": currentDateString(),
        "result": {
            "ibm": ibmEvaluation,
            "google": googleEvaluation,
            "googleSpecial": googleEvaluationSpecial,
            "amazon": amazonEvaluation
        },
        "ground_truth": {
            "sentence": testSentence,
            "annotation": tokens
        },
        "provider_response": testResult,
        "runtime_Env": {"python_version": "Python 3.7.5 64-bit",
                        "machine_info": "MacBookPro16,1 | 2,3 GHz 8-Core Intel Core i9 | 64 GB 2667 MHz DDR4",
                        "available_ram": str(round(psutil.virtual_memory().available/float(1 << 20)))+" MB / 65536 MB",
                        "internet_router": "Vodafone Docsis 3.1 | 01.01.117.01.EURO",
                        "internet_speed": "Down: 100 Mbit/s | Up: 50 Mbit/s",
                        "internet_connection_type": "Wi-Fi",
                        "geo_location": "Berlin, Germany",
                        "parallel_requests": "false"},
        "failed": failed,
        "nlp_library_versions": {"ibm": "ibm-cloud-sdk-core-1.5.1 ibm-watson-4.3.0",
                                 "google": "google-api-core-1.15.0 google-cloud-language-1.3.0",
                                 "microsoft": "azure-core-1.2.2 azure-ai-textanalytics-1.0.0b2",
                                 "amazon": "awscli-1.18.5 boto3-1.12.5"}
    })
    print("Deleting test from copy ...")
    sourceDb.delete_one({"_id": test["_id"]})
    print("Done.")


def nvTestOne():
    """
    Performs all the calls to evaluate a provider's response to a Noun-Verb test sentence and retores all results in a local MongoDB database.
    """
    
    print("Getting NV test ...")
    test = nvGetTest()
    testSentence = test['sentence']
    tokens = test['annotation']

    print("Testing ...")
    testResult = ServiceCalls.makeCalls(testSentence)

    failed = 0
    if len(testResult['values']['ibm']['tokens']) == 0:
        failed = 1
    if len(testResult['values']['google']['tokens']) == 0:
        failed = 1
    if len(testResult['values']['amazon']['tokens']) == 0:
        failed = 1

    ibmEvaluation = {}
    googleEvaluation = {}
    amazonEvaluation = {}

    if failed == 0:
        ibmEvaluation = evaluateNV(
            tokens['token_text'], tokens['pos_tag'], testResult['values']['ibm']['tokens'])
        googleEvaluation = evaluateNV(
            tokens['token_text'], tokens['pos_tag'], testResult['values']['google']['tokens'])
        amazonEvaluation = evaluateNV(
            tokens['token_text'], tokens['pos_tag'], testResult['values']['amazon']['tokens'])

    print("Storing ...")
    nvEvaluationResults.insert_one({
        "test_id": test['_id'],
        "test_date": currentDateString(),
        "result": {
            "ibm": ibmEvaluation,
            "google": googleEvaluation,
            "amazon": amazonEvaluation
        },
        "ground_truth": {
            "sentence": testSentence,
            "annotation": tokens
        },
        "provider_response": testResult,
        "runtime_Env": {"python_version": "Python 3.7.5 64-bit",
                        "machine_info": "MacBookPro16,1 | 2,3 GHz 8-Core Intel Core i9 | 64 GB 2667 MHz DDR4",
                        "available_ram": str(round(psutil.virtual_memory().available/float(1 << 20)))+" MB / 65536 MB",
                        "internet_router": "Vodafone Docsis 3.1 | 01.01.117.01.EURO",
                        "internet_speed": "Down: 100 Mbit/s | Up: 50 Mbit/s",
                        "internet_connection_type": "Wi-Fi",
                        "geo_location": "Berlin, Germany",
                        "parallel_requests": "false"},
        "failed": failed,
        "nlp_library_versions": {"ibm": "ibm-cloud-sdk-core-1.5.1 ibm-watson-4.3.0",
                                 "google": "google-api-core-1.15.0 google-cloud-language-1.3.0",
                                 "microsoft": "azure-core-1.2.2 azure-ai-textanalytics-1.0.0b2",
                                 "amazon": "awscli-1.18.5 boto3-1.12.5"}
    })
    print("Deleting test from copy ...")
    nvGroundTruthCopy.delete_one({"_id": test["_id"]})
    print("Done.")


# Example Usage:

#while 1:
#    udTestOne(udGetTest(), udGroundTruthCopy, udEvaluationResults)
#    udTestOne(udPTGetTest(), udPTGroundTruthCopy, udPTEvaluationResults)
#    udTestOne(udEWGetTest(), udEWGroundTruthCopy, udEWEvaluationResults)
#    nvTestOne()

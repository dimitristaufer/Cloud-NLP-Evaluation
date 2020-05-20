import sys
sys.path.append('../')
sys.path.append('../..')
import json
from datetime import datetime
from bson import json_util
import psutil
from mongo_connect import Connect
from ground_truth_working_copy import updateWorkingCopy
import entity_recognition_calls as ServiceCalls
import unknown_words

updateWorkingCopy() # copies untested documents from the groundTruth MongoDB collection to the gtWorkingCopy collection. This way we were able to collect new documents, while simultaneously testing and deleteting others.

### Mongo DB Init ###
connection = Connect.get_connection()

db = connection.entityRecognition
gtWorkingCopy = db.gtWorkingCopy
gtWorkingCopyTested = db.gtWorkingCopyTested
evaluationResults = db.evaluationResults
###               ###


def currentDateString():
    """
    Gets the current date and time as string.

    Returns:
        String -- The current date and time
    """
    
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def getTests():
    """Returns a dictionary of document samples for the Entity Types Person, Location, and Organization.

    Returns:
        [type] -- Returns a dictionary of document samples for the Entity Types Person, Location, and Organization.
    """

    personDocument = gtWorkingCopy.find_one({"$and": [{'entity_type': 'Person'}, {'sentences.5': {'$exists': True}}]})  # Person and at least 5 test sentences
    locationDocument = gtWorkingCopy.find_one({"$and": [{'entity_type': 'Location'}, {'sentences.5': {'$exists': True}}]})  # Location and at least 5 test sentences
    organizationDocument = gtWorkingCopy.find_one({"$and": [{'entity_type': 'Organization'}, {'sentences.5': {'$exists': True}}]})  # Organization and at least 5 test sentences
    tests = {"person": personDocument,
             "location": locationDocument,
             "organization": organizationDocument}
    return tests


def runTests():
    """
    Performs all necessary calls to retrieve, test, and evaluate a test document from a local MongoDB database and then stores the results in a MongoDB collection.
    """
    
    print("... getting new tests ...")
    rawTests = getTests()
    tests = json.loads(json_util.dumps(getTests()))
    for i, test in tests.items():
        print("--- running test --- '" +
              test['entity'] + "', of type: '" + test['entity_type'] + "' " + u'\U0001F9EA')
        testSentencesInfo = []
        testSentences = []
        for j in range(0, 5):  # test 5 sentences containing this Entity
            testSentences.append(test['sentences'][j])
            testSentencesInfo.append({  # create testSentenceInfo data with meta information on the sentence
                "character_count": len(test['sentences'][j]['sentence']),
                "unknown_words": unknown_words.measureUnknownWords(test['sentences'][j]['sentence']),
                "sentence": test['sentences'][j]['sentence'],
                "didRecognizeBoth": {
                    "ibm": True,
                    "google": True,
                    "microsoft": True,
                    "amazon": True
                }
            })

        isMultiwordEntityName = False
        if " " in test['entity']:
            isMultiwordEntityName = True

        testOutcome = {
            "test_date": currentDateString(),
            "target_entity": test['entity'],
            "target_entity_type": test['entity_type'],
            "multiword_entity": isMultiwordEntityName,
            "tested_sentences": testSentencesInfo,
            "overall_results": {
                "ibm": {},
                "google": {},
                "microsoft": {},
                "amazon": {}
            },
            "detailed_results": [],
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
        }
        # test 5 sentences containing this Entity
        for k, testSentence in enumerate(testSentences):
            print("... calling APIs ...")
            responseAndSentence = (
                {"sentence_data": testSentence, "response": ServiceCalls.makeCalls(testSentence['sentence'])})
            print("... called APIs ... " + u'\u2705')
            detailedResult = makeResult(
                targetEntity=test['entity'], targetEntityType=test['entity_type'], responseAndSentence=responseAndSentence)
            testOutcome['detailed_results'].append(detailedResult)

            # After having created the detailedResults, we would like to add a field 'didRecognizeBoth' to the 'testSentences' field
            for providerResult in detailedResult['providerResults']:
                for provider, presult in providerResult.items():
                    if not presult[0]['didRecognizeBoth']:
                        testOutcome['tested_sentences'][k]['didRecognizeBoth'][provider] = False

        testOutcome = makeTotalResult(
            testOutcome, test['entity'], test['entity_type'])

        evaluationResults.insert_one(testOutcome)
        gtWorkingCopyTested.insert_one(rawTests[i])
        gtWorkingCopy.delete_one({'_id': rawTests[i]['_id']})

        print("--- finished test " + u'\U0001F4AA' + " ---")

        #print(json.dumps(testOutcome, indent=4, sort_keys=False))
        # sys.exit() # only perform the first test (person)


# calculate and add the total number of failed sentences etc. per provider
def makeTotalResult(testOutcome, targetEntity, targetEntityType):
    """After having called makeResult() for the five sentences, this function calculates the total number of failed sentences and more.

    Arguments:
        testOutcome {Dictionary} -- The test outcome from makeResults()
        targetEntity {String} -- The ground-truth named entity
        targetEntityType {String} -- The ground-truth named entity type

    Returns:
        Dictionary -- A modified copy of the tests outcome with added information on the total results
    """
    
    print("... calculating total results ...")
    testOutcomeCopy = testOutcome.copy()
    ibmFailedOneSentence = False
    ibmFailedSentencesCount = 0
    ibmPtFailedSentencesCount = 5
    googleFailedOneSentence = False
    googleFailedSentencesCount = 0
    googlePtFailedSentencesCount = 5
    microsoftFailedOneSentence = False
    microsoftFailedSentencesCount = 0
    microsoftPtFailedSentencesCount = 5
    amazonFailedOneSentence = False
    amazonFailedSentencesCount = 0
    amazonPtFailedSentencesCount = 5
    for sentenceTest in testOutcome['detailed_results']:
        for providerResult in sentenceTest['providerResults']:
            for provider, presult in providerResult.items():
                if not presult[0]['didRecognizeBoth']:
                    if provider == 'ibm':
                        ibmFailedOneSentence = True
                        ibmFailedSentencesCount += 1
                    elif provider == 'google':
                        googleFailedOneSentence = True
                        googleFailedSentencesCount += 1
                    elif provider == 'microsoft':
                        microsoftFailedOneSentence = True
                        microsoftFailedSentencesCount += 1
                    elif provider == 'amazon':
                        amazonFailedOneSentence = True
                        amazonFailedSentencesCount += 1

                ### Partially Correct ###
                if provider == 'ibm':
                    print(presult[0])
                    entities = presult[0]['providerReponse']['entities']
                    ptExists = False
                    for entityObject in entities:
                        recognizedEntity = entityObject['entity']
                        recognizedEntityType = entityObject['type']
                        if recognizedEntity in targetEntity and recognizedEntityType == targetEntityType:
                            ptExists = True
                    if ptExists:
                        ibmPtFailedSentencesCount -= 1
                if provider == 'google':
                    entities = presult[0]['providerReponse']['entities']
                    ptExists = False
                    for entityObject in entities:
                        recognizedEntity = entityObject['entity']
                        recognizedEntityType = entityObject['type']
                        if recognizedEntity in targetEntity and recognizedEntityType == targetEntityType:
                            ptExists = True
                    if ptExists:
                        googlePtFailedSentencesCount -= 1
                if provider == 'microsoft':
                    entities = presult[0]['providerReponse']['entities']
                    ptExists = False
                    for entityObject in entities:
                        recognizedEntity = entityObject['entity']
                        recognizedEntityType = entityObject['type']
                        if recognizedEntity in targetEntity and recognizedEntityType == targetEntityType:
                            ptExists = True
                    if ptExists:
                        microsoftPtFailedSentencesCount -= 1
                if provider == 'amazon':
                    entities = presult[0]['providerReponse']['entities']
                    ptExists = False
                    for entityObject in entities:
                        recognizedEntity = entityObject['entity']
                        recognizedEntityType = entityObject['type']
                        if recognizedEntity in targetEntity and recognizedEntityType == targetEntityType:
                            ptExists = True
                    if ptExists:
                        amazonPtFailedSentencesCount -= 1

    testOutcome['overall_results']['ibm']['recognizedAllSentences'] = not ibmFailedOneSentence
    testOutcome['overall_results']['ibm']['failedSentences_count'] = ibmFailedSentencesCount
    testOutcome['overall_results']['ibm']['failedSentences_percentage'] = ibmFailedSentencesCount / 5
    testOutcome['overall_results']['ibm']['pt_failedSentences_count'] = ibmPtFailedSentencesCount
    testOutcome['overall_results']['ibm']['pt_failedSentences_percentage'] = ibmPtFailedSentencesCount / 5
    testOutcome['overall_results']['google']['recognizedAllSentences'] = not googleFailedOneSentence
    testOutcome['overall_results']['google']['failedSentences_count'] = googleFailedSentencesCount
    testOutcome['overall_results']['google']['failedSentences_percentage'] = googleFailedSentencesCount / 5
    testOutcome['overall_results']['google']['pt_failedSentences_count'] = googlePtFailedSentencesCount
    testOutcome['overall_results']['google']['pt_failedSentences_percentage'] = googlePtFailedSentencesCount / 5
    testOutcome['overall_results']['microsoft']['recognizedAllSentences'] = not microsoftFailedOneSentence
    testOutcome['overall_results']['microsoft']['failedSentences_count'] = microsoftFailedSentencesCount
    testOutcome['overall_results']['microsoft']['failedSentences_percentage'] = microsoftFailedSentencesCount / 5
    testOutcome['overall_results']['microsoft']['pt_failedSentences_count'] = microsoftPtFailedSentencesCount
    testOutcome['overall_results']['microsoft']['pt_failedSentences_percentage'] = microsoftPtFailedSentencesCount / 5
    testOutcome['overall_results']['amazon']['recognizedAllSentences'] = not amazonFailedOneSentence
    testOutcome['overall_results']['amazon']['failedSentences_count'] = amazonFailedSentencesCount
    testOutcome['overall_results']['amazon']['failedSentences_percentage'] = amazonFailedSentencesCount / 5
    testOutcome['overall_results']['amazon']['pt_failedSentences_count'] = amazonPtFailedSentencesCount
    testOutcome['overall_results']['amazon']['pt_failedSentences_percentage'] = amazonPtFailedSentencesCount / 5
    return testOutcomeCopy


def makeResult(targetEntity, targetEntityType, responseAndSentence):
    """Evaluates each provider's reponse to an NER call by checking whether the target named entity and its type were correctly annotated by the provider.

    Arguments:
        targetEntity {String} -- The ground-truth named entity
        targetEntityType {String} -- The ground-truth named entity type
        responseAndSentence {Dictionary} -- The NLP provider's reponse and the sentence that was tested

    Returns:
        Dictionary -- The results of the evaluation, including whether a provider recognized the named entity, its type, or both
    """
    
    print("... making results ...")
    result = {
        "testSentence": responseAndSentence['sentence_data'],
        "providerResults": [],
        "failed": False
    }
    for provider, providerResponse in responseAndSentence['response']['values'].items():
        providerResults = []
        # did not recognize any Entities
        if len(providerResponse['entities']) == 0 and responseAndSentence['response']['errors'][provider] == "":
            providerResults.append({
                "didRecognizeEntity": False,
                "didRecognizeEntityType": False,
                "didRecognizeBoth": False,
                "recognizedZeroEntities": True,
                "providerReponse": providerResponse})
        elif len(providerResponse['entities']) == 0 and responseAndSentence['response']['errors'][provider] != "":  # error
            providerResults.append({
                "didRecognizeEntity": False,
                "didRecognizeEntityType": False,
                "didRecognizeBoth": False,
                "recognizedZeroEntities": True,
                "providerReponse": providerResponse})
            result["failed"] = True  # mark this test as failed

        else:
            didRecognizeEntity = False
            didrecognizeEntityType = False

            for recognizedEntity in providerResponse['entities']:
                # e.g. 'Dimitri Staufer' and 'Event'
                if (recognizedEntity['entity'] == targetEntity) and (recognizedEntity['type'] != targetEntityType):
                    didRecognizeEntity = True
                # e.g. 'Dimitri Staufer' and 'Person'
                elif (recognizedEntity['entity'] == targetEntity) and (recognizedEntity['type'] == targetEntityType):
                    didRecognizeEntity = True
                    didrecognizeEntityType = True

            providerResults.append({
                "didRecognizeEntity": didRecognizeEntity,
                "didRecognizeEntityType": didrecognizeEntityType,
                "didRecognizeBoth": (didRecognizeEntity and didrecognizeEntityType),
                "recognizedZeroEntities": False,
                "providerReponse": providerResponse
            })

        result['providerResults'].append({
            provider: providerResults
        })

    return result

# Example Usage:

# while 1:
#    runTests()

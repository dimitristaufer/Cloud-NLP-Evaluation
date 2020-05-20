from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential  # v3.0

subscription_key1 = "..."
endpoint1 = "https://project1.cognitiveservices.azure.com/"

subscription_key2 = "..."
endpoint2 = "https://project2.cognitiveservices.azure.com/"


def authenticateClientv3():
    ta_credential = TextAnalyticsApiKeyCredential(subscription_key1)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint1, credential=ta_credential)
    return text_analytics_client

class Sentiment:
    """
    A class containing the returned sentiment values and error message from a provider.
    """
    def __init__(self, value, errorMessage):
        self.value = value
        self.errorMessage = errorMessage

class Entities:
    """
    A class containing the returned NER values and error message from a provider.
    """
    def __init__(self, values, errorMessage):
        self.values = values
        self.errorMessage = errorMessage


'''
Uncomment this and comment the 'analyzeEntities' function to analyze Sentiment. 
Using Version 2 and 3 together causes errors. We use version 3 with Entity recognition, 
because there are more available Entity Types.

def authenticateClientv2():
    credentials = CognitiveServicesCredentials(subscription_key1)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint1, credentials=credentials)
    return text_analytics_client

def analyzeSentiment(text):
    documents = [{"id": "1", "language": "en", "text": text}]

    try:
        client = authenticateClientv2()
        response = client.sentiment(documents=documents)
        for document in response.documents:
            # print("Document Id: ", document.id, ", Sentiment Score: ", "{:.2f}".format(document.score))
            return(Sentiment(document.score, ""))

    except Exception as e:
        return(Sentiment(-999, str(e)))
'''


def analyzeEntities(text):
    """
    Uses the NLP provider's SDK to perform an NER operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    client = authenticateClientv3()
    try:
        documents = [text]
        response = client.recognize_entities(inputs=documents)[0]
        formattedEntities = []
        for entity in response.entities:
            formattedEntities.append(
                {'entity': entity.text, 'type': entity.category})
        normalizedEntities = normalizeEntities(formattedEntities)
        return Entities(normalizedEntities, "")
    except Exception as e:
        return Entities([], str(e))


def normalizeEntities(formattedEntities):
    """
    Normalizes the provider's entity types to match the ones used in our evaluation.

    Arguments:
        formattedEntities {List} -- List of recognized named entities and their types.

    Returns:
        List -- A copy of the input list with modified entity types.
    """
    fEcopy = formattedEntities
    for i in range(len(fEcopy)):
        if fEcopy[i]['type'] == "Person":
            fEcopy[i]['type'] = "Person"
        elif fEcopy[i]['type'] == "Location":
            fEcopy[i]['type'] = "Location"
        elif fEcopy[i]['type'] == "Organization":
            fEcopy[i]['type'] = "Organization"
        elif fEcopy[i]['type'] == "Event":
            fEcopy[i]['type'] = "Event"
        elif fEcopy[i]['type'] == "Product":
            fEcopy[i]['type'] = "Product"
    return fEcopy


# print(analyzeSentiment("I don't like this job all the time, sometimes i like it.").value)
#print(analyzeEntities("I work at the company Apple in California with Donald Trump"))

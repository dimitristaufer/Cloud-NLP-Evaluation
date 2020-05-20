import json
import boto3

comprehend = boto3.client(service_name='comprehend',
                          region_name='us-east-1')


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
        
class Syntax:
    """
    A class containing the returned POS values and error message from a provider.
    """
    def __init__(self, values, errorMessage):
        self.values = values
        self.errorMessage = errorMessage


def analyzeSentiment(text):
    """
    Uses the NLP provider's SDK to perform a sentiment analysis operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    try:
        resultDict = json.dumps(
            comprehend.detect_sentiment(Text=text, LanguageCode='en'))
        scores = json.loads(resultDict)['SentimentScore']
        return(Sentiment(normalizeSentiment(scores), ""))
    except Exception as e:
        return(Sentiment(-999, str(e)))


def normalizeSentiment(scores):
    """
    Normalizes the provider's polarity score the match the format of our thesis.

    Arguments:
        sentiment {Double} -- Polarity score

    Returns:
        Double -- Normalized polarity score
    """
    return (1 * scores['Positive'])+(0.5 * (scores['Neutral'] + scores['Mixed']))+(0 * scores['Negative'])


def analyzeEntities(text):
    """
    Uses the NLP provider's SDK to perform an NER operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    try:
        resultDict = json.dumps(
            comprehend.detect_entities(Text=text, LanguageCode='en'))
        entities = json.loads(resultDict)["Entities"]
        formattedEntities = []
        for entity in entities:
            formattedEntities.append({'entity': entity['Text'], 'type': entity['Type']})
            
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
        if fEcopy[i]['type'] == "PERSON":
            fEcopy[i]['type'] = "Person"
        elif fEcopy[i]['type'] == "LOCATION":
            fEcopy[i]['type'] = "Location"
        elif fEcopy[i]['type'] == "ORGANIZATION":
            fEcopy[i]['type'] = "Organization"
        elif fEcopy[i]['type'] == "EVENT":
            fEcopy[i]['type'] = "Event"
        elif fEcopy[i]['type'] == "COMMERCIAL_ITEM":
            fEcopy[i]['type'] = "Product"
    return fEcopy

def analyzeSyntax(text):
    """
    Uses the NLP provider's SDK to perform an Part-of-Speech tagging (Syntax Analysis) operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    
    try:
        response = comprehend.detect_syntax(Text=text, LanguageCode='en')
        syntaxTokens = response['SyntaxTokens']

        values = []
        for token in syntaxTokens:
            tokenText = token['Text']
            tokenBeginOffset = token['BeginOffset']
            tokenTag = token['PartOfSpeech']['Tag']
            if tokenTag == "O":
                tokenTag = "X"
            values.append({
                "token_text" : tokenText,
                "token_begin_offset" : tokenBeginOffset,
                "pos_tag" : tokenTag
            })
            
        return Syntax(values, "")
    except Exception as e:
        return Syntax([], str(e))


#print(analyzeSentiment(u"I hate you so much!").value)
#print(analyzeEntities(u"My name is Donals Drump and today is independence day at Microsoft"))
#print(json.dumps(analyzeSyntax(u"Carly , confused about the situation , questions Nevel on how he won the contest .").values, sort_keys=True, indent=4))

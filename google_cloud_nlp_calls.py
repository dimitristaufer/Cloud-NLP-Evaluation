import os
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/.json"

client = language.LanguageServiceClient()

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


class Classiciation:
    """
    A class containing the returned classification values and error message from a provider.
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
    
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='en')

    try:
        response = client.analyze_sentiment(document=document)
        overallSentiment = response.document_sentiment.score
        return Sentiment(normalizeSentiment(overallSentiment), "")
    except Exception as e:
        return Sentiment(-999, str(e))


def normalizeSentiment(sentiment):
    """
    Normalizes the provider's polarity score the match the format of our thesis.

    Arguments:
        sentiment {Double} -- Polarity score

    Returns:
        Double -- Normalized polarity score
    """
    return (sentiment + 1) * 0.5


def analyzeEntities(text):
    """
    Uses the NLP provider's SDK to perform an NER operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    try:
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT,
            language='en')
        response = client.analyze_entities(document=document)
        formattedEntities = []
        for entity in response.entities:
            formattedEntities.append(
                {'entity': entity.name, 'type': enums.Entity.Type(entity.type).name})

        normalizedEntities = normalizeEntities(formattedEntities)
        return Entities(normalizedEntities, "")
    except Exception as e:
        return Entities([], str(e.args))


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
        elif fEcopy[i]['type'] == "CONSUMER_GOOD":
            fEcopy[i]['type'] = "Product"
    return fEcopy


def analyzeSyntax(text):
    """
    Uses the NLP provider's SDK to perform an Part-of-Speech tagging (Syntax Analysis) operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='en')

    try:
        response = client.analyze_syntax(
            document=document, encoding_type='UTF8')

        values = []
        for token in response.tokens:
            tokenText = token.text.content
            tokenBeginOffset = token.text.begin_offset
            tokenTag = u"{}".format(enums.PartOfSpeech.Tag(
                token.part_of_speech.tag).name)
            if tokenTag == "CONJ":
                tokenTag = "CCONJ"
            if tokenTag == "PRT":
                tokenTag = "PART"
            values.append({
                "token_text": tokenText,
                "token_begin_offset": tokenBeginOffset,
                "pos_tag": tokenTag
            })

        return Syntax(values, "")
    except Exception as e:
        return Syntax([], str(e.args))


def classifyContent(text):
    """
    Uses the NLP provider's SDK to perform a content classification operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='en')

    try:
        response = client.classify_text(document=document)

        values = []
        for category in response.categories:
            values.append({
                "category": category.name,
                "confidence": category.confidence
            })
        return(Classiciation(values, ""))
    except Exception as e:
        return Classiciation([], str(e.args))


# print('\n\n')
# print(analyzeSentiment(u"I hate this job.").value)
#print(analyzeEntities(u"My name is Donald Trump and I am using a MacBook in California during World War II at Microsoft"))
#print(json.dumps(analyzeSyntax(u"Carly , confused about the situation , questions Nevel on how he won the contest .").values, sort_keys=True, indent=4))
#print(classifyContent(u'The 70-200mm f/2.8 is one of the most important lenses for many photographers and videographers, as they are typically of high optical quality and offer a very versatile focal length range coupled with a wide maximum aperture for a zoom. This excellent video review takes a look at the new Canon RF 70-200mm f/2.8L IS USM and what you can expect from it both in terms of performance and image quality.').values)

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, EntitiesOptions, CategoriesOptions, SyntaxOptions, SyntaxOptionsTokens
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator('...')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    authenticator=authenticator
)

natural_language_understanding.set_service_url(
    'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/...')

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
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions())).get_result()
        return Sentiment(normalizeSentiment(json.loads(json.dumps(response))['sentiment']['document']['score']), "")
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
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(entities=EntitiesOptions(limit=500))).get_result()

        rawEntities = json.loads(json.dumps(response))['entities']
        formattedEntities = []

        for entity in rawEntities:
            formattedEntities.append(
                {'entity': entity['text'], 'type': entity['type']})

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
        elif fEcopy[i]['type'] == "Company" or fEcopy[i]['type'] == "Organization":
            fEcopy[i]['type'] = "Organization"
        elif fEcopy[i]['type'] == "Event" or fEcopy[i]['type'] == "NaturalEvent" or fEcopy[i]['type'] == "SportingEvent":
            fEcopy[i]['type'] = "Event"
        elif fEcopy[i]['type'] == "ConsumerProduct":
            fEcopy[i]['type'] = "Product"
    return fEcopy


def analyzeSyntax(text):
    """
    Uses the NLP provider's SDK to perform an Part-of-Speech tagging (Syntax Analysis) operation.

    Arguments:
        text {String} -- Text to be analyzed.
    """
    
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(
                syntax=SyntaxOptions(
                    sentences=False,
                    tokens=SyntaxOptionsTokens(
                        lemma=False,
                        part_of_speech=True,
                    )))).get_result()
        syntaxTokens = response['syntax']['tokens']

        values = []
        for token in syntaxTokens:
            tokenText = token['text']
            tokenBeginOffset = token['location'][0]
            tokenTag = token['part_of_speech']
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
    
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(categories=CategoriesOptions())).get_result()

        values = []
        for category in response["categories"]:
            values.append({
                "category": category["label"],
                "confidence": category["score"]
            })
        return Classiciation(values, "")
    except Exception as e:
        return Classiciation([], str(e.args))


# print('\n\n')
#print(analyzeSentiment(u"I hate it so much.").value)
#print(analyzeEntities("Tonight is the full moon and we will look at the Aurora. There is a Tsunami coming your way. The FIFA World Cup is not taking place, neither are the Summer Olympic Games."))
#print(json.dumps(analyzeSyntax(u"Carly , confused about the situation , questions Nevel on how he won the contest .").values, sort_keys=True, indent=4))
#print(classifyContent(u"The 70-200mm f/2.8 is one of the most important lenses for many photographers and videographers, as they are typically of high optical quality and offer a very versatile focal length range coupled with a wide maximum aperture for a zoom. This excellent video review takes a look at the new Canon RF 70-200mm f/2.8L IS USM and what you can expect from it both in terms of performance and image quality.'").values)

from nltk import word_tokenize

NEGATE = [ # source https://www.nltk.org/_modules/nltk/sentiment/vader.html
    "aint",
    "arent",
    "cannot",
    "cant",
    "couldnt",
    "darent",
    "didnt",
    "doesnt",
    "ain't",
    "aren't",
    "can't",
    "couldn't",
    "daren't",
    "didn't",
    "doesn't",
    "dont",
    "hadnt",
    "hasnt",
    "havent",
    "isnt",
    "mightnt",
    "mustnt",
    "neither",
    "don't",
    "hadn't",
    "hasn't",
    "haven't",
    "isn't",
    "mightn't",
    "mustn't",
    "neednt",
    "needn't",
    "never",
    "none",
    "nope",
    "nor",
    "not",
    "nothing",
    "nowhere",
    "oughtnt",
    "shant",
    "shouldnt",
    "uhuh",
    "wasnt",
    "werent",
    "oughtn't",
    "shan't",
    "shouldn't",
    "uh-uh",
    "wasn't",
    "weren't",
    "without",
    "wont",
    "wouldnt",
    "won't",
    "wouldn't",
    "rarely",
    "seldom",
    "despite",
]


def measureNegations(text):
    """
    This method finds negations in a text and returns their count, percentage and values.
    
    Arguments:
        text {String} -- the text to be processed.
    
    Returns:
        Dictionary -- a dictionary containing the count, percentage and values of negations.
    """
    wds = word_tokenize(text)
    wdCount = len(wds)
    negCount = 0
    negs = ""
    for wd in wds:
        if wd in NEGATE:
            negCount += 1
            negs += wd+", "
    if len(negs) >= 2:
        negs = negs[:-2]  # remove ", " at the end
    return {"count" : negCount,
            "values" : negs,
            "percentage" : round(negCount/wdCount, 2)}

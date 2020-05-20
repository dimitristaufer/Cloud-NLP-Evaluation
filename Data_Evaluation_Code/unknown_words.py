from nltk import word_tokenize
import enchant

def measureUnknownWords(text):  # also counts and lists multiple occurrences
    """
    Counts the number of unknown words in a text, according to the enchant dictionary.

    Arguments:
        text {String} -- The text to be analyzed.

    Returns:
        Dictionary -- A dictionary containing the number of unknown words, the words themselves, and the percentage relative to the sentence's word count
    """
    us = enchant.Dict("en_US")
    uk = enchant.Dict("en_US")
    wds = word_tokenize(text)
    wdCount = len(wds)
    ukncount = 0
    words = ""
    for wd in wds:
        if not us.check(wd) and not uk.check(wd) and len(wd) > 1:
            ukncount += 1
            words += wd+", "
    if len(words) >= 2:
        words = words[:-2]  # remove ", " at the end
    return {"count": ukncount,
            "words": words,
            "percentage": round(ukncount/wdCount, 2)}

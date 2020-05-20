import hashlib
import requests
from readability import Document
from bs4 import BeautifulSoup

def getTestSentences(entity, entityType):
    """
    Scrapes Google News for news articles that include a specified named entity and entity type and splits these news articles into sentences.
    
    Returns:
        Dictionary -- A dictionary containing the named entity, the entity type, and the retrieved sentences.
    """
    
    print("... getting Google News results for '" + entity + "' ...")

    url = "https://www.google.com/search?q=%22"+entity + \
"%22+"+entityType+"&tbm=nws&num=100&cr=countryUS"
    # Google News query with the entity name in double quotes and the type without quotes
    # Show 100 results to limit the number of requests
    # Filter by "countryUS" to (more or less) only have English texts, even for non-english entities, e.g. "Angela Merkel"

    resultDic = {"entity": entity,
                 "entityType": entityType,
                 "sentences": []}

    try:
        response = requests.get(url, timeout=20, headers={  # in order to bypass security
            'accept-language': 'en-US,en;q=0.9,de;',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
        })
    except Exception as e:
        print("Error 1: " + str(e.args))
        return resultDic

    htmlString = response.text
    bs = BeautifulSoup(htmlString, "lxml")
    # print(bs)
    newsLinks = bs.find_all("a")  # find all links on the Google News webpage
    # print(wikiLinks)
    parsedLinks = []
    for link in newsLinks:  # get hrefs and remove invalid urls
        href = str(link.get("href"))
        # links that do not contain 'http' are internal Google links, links that contain google are external Google link
        if "http" in href and "google" not in href and href not in parsedLinks:
            # the link is an external URL (very likely a news article)
            parsedLinks.append(href)
            # print(href)

    if len(parsedLinks) == 0:
        print("! Google reCaptcha or found exactly zero results !")

    print("... reading and parsing news articles ...")

    for link in parsedLinks:  # get the news articles for each link
        try:
            response = requests.get(link, timeout=10, headers={  # in order to bypass security
                'accept-language': 'en-US,en;q=0.9,de;',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
            })

            doc = Document(response.text)
            cleanWebsiteText = ""
            websiteText = ""
            try:
                # extract the article text from news website
                websiteText = BeautifulSoup(
                    doc.summary(), features="lxml").get_text()
            except Exception as e:
                print("Error 2: " + str(e.args))
                continue

            if len(websiteText) != 0:
                for line in iter(websiteText.splitlines()):
                    if len(line) > 50:
                        # remove blank lines and only allow texts with 50 or more characters
                        cleanWebsiteText = cleanWebsiteText+line
                    else:
                        continue

            testSentences = [sentence.replace("  ", "") + '.' for sentence in cleanWebsiteText.split(
                '.') if entity in sentence]  # extract all sentences that contain the passed entity name

            # remove unwanted white spaces from the sentences
            for i in range(len(testSentences)):
                testSentence = testSentences[i]
                if testSentence.startswith(" "):
                    testSentence = testSentence[1:]
                if testSentence.endswith(" "):
                    testSentence = testSentence[:-1]
                testSentences[i] = testSentence

            if len(testSentences) != 0:  # check if valid sentences are left over
                for testSentence in testSentences:  # create a unique id for each sentence and add it to the resultDic alongside the source url
                    sentenceId = hashlib.md5(
                        testSentence.encode('utf-8')).hexdigest()
                    url = link
                    entry = {"id": sentenceId,
                             "url": link,
                             "sentence": testSentence}
                    resultDic["sentences"].append(entry)

        except Exception as e:
            print("Error 3: " + str(e.args))
            continue

    return resultDic

#print(json.dumps(getTestSentences("Donald Trump", "Person"), indent=4, sort_keys=True))

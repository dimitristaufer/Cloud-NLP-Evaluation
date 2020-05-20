import requests
from readability import Document
from bs4 import BeautifulSoup

def readArticle(url):
    """Scrapes an news article's text and parses it using BeautifulSoup.

    Arguments:
        url {String} -- The article's URL

    Returns:
        Dictionary -- A dictionary containing the news article's title and text.
    """
    
    print("... parsing tweet URL ...")

    try:
        response = requests.get(url, timeout=10, headers={  # in order to bypass security
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        })
    except Exception as e:
        print("Error: " + str(e.args))
        return { # if something went wrong, we always return a dictionary with empty string values
            "site_title": "",
            "site_article": ""
        }

    cleanWebsiteTitle = ""
    doc = Document(response.text)
    try:
        cleanWebsiteTitle = doc.short_title() # try getting the articles title
    except Exception as e:
        print("Error: " + str(e.args))

    if cleanWebsiteTitle == "": # Error (usually because the news website uses some form of bot detection)
        try:
            response = requests.get(url, timeout=10) # try using no headers (works better with certain website types)
        except Exception as e:
            print("Error: " + str(e.args))
            return {
                "site_title": "",
                "site_article": ""
            }
        doc = Document(response.text)
        try:
            cleanWebsiteTitle = doc.short_title() # try getting the articles title (again)
        except Exception as e:
            print("Error: " + str(e.args))
            return {
                "site_title": "",
                "site_article": ""
            }


    cleanWebsiteText = ""
    websiteText = ""
    try:
        websiteText = BeautifulSoup(doc.summary(), features="lxml").get_text() # extract the article text from news website
    except Exception as e:
        print("Error: " + str(e.args))
        return {
            "site_title": "",
            "site_article": ""
        }
    
    if len(websiteText) != 0:
        for line in iter(websiteText.splitlines()):
            if len(line) > 50:
                cleanWebsiteText = cleanWebsiteText+line # remove blank lines and only allow texts with 50 or more characters

    if cleanWebsiteText == "": # the article text could not be extracted
        return {
            "site_title": "",
            "site_article": ""
        }

    # check for HTTP errors
    if ("400" in cleanWebsiteTitle) or ("401" in cleanWebsiteTitle) or ("403" in cleanWebsiteTitle) or ("404" in cleanWebsiteTitle) or ("500" in cleanWebsiteTitle) or ("502" in cleanWebsiteTitle) or ("503" in cleanWebsiteTitle) or ("504" in cleanWebsiteTitle):
        return {
            "site_title": "",
            "site_article": ""
        }
        
    if "Denied" in cleanWebsiteText: # we might loose some article texts about something being 'denied' ;)
        return {
            "site_title": "",
            "site_article": ""
        }

    if len(cleanWebsiteText) < 130: # we define all article texts under 130 characters as invalid
        return {
            "site_title": "",
            "site_article": ""
        }

    return {
        "site_title": cleanWebsiteTitle,
        "site_article": cleanWebsiteText
    }

#print(readArticle(""))

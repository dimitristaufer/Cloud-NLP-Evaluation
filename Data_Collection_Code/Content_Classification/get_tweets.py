import re
from twython import Twython
import twitter

### Twitter Dev Authentication ###
api = twitter.Api(consumer_key='...',
                  consumer_secret='...',
                  access_token_key='...',
                  access_token_secret='...')

twt = Twython('...', '...',
              '...', '...')
twt.verify_credentials() 
###                            ###


def alreadyFoundURL(results, url):
    """
    Checks whether a url String has already been found before, to prevent duplicates.
    
    Returns:
        Boolean -- True, if the specified URL has already been found, False, if not.
    """
    for result in results:
        if url in result[1]:
            return True
    return False

def getData(hashtag, numberResults = 30):
    """
    Searches Twitter.com for tweets that contain a specified hashtag and also an external url that contains the string 'news' or 'blog'.
    
    Returns:
        List -- A list, containing an external URL from a tweet that tweet's included hashtags.
    """
    tweetsToBeFetched = numberResults
    if numberResults < 30:
        tweetsToBeFetched = 30 # we define the minimum fetch amount as 30 tweets (because the number of requests could be limited)
    
    MAX_TRIES = 10 # default 10 retries (probably to high)
    tweets = []

    for i in range(0, MAX_TRIES):
        if tweetsToBeFetched < len(tweets):
            break

        # twitter API search query for tweets with the 'hashtag' and an url containing the string 'news' or 'blog', without retweets and other twitter media, language: English
        if 0 == i: # first page
            results = twt.search(q="#"+hashtag+" AND url:news OR url:blog AND -url:bit AND -filter:retweets AND -filter:media AND -filter:native_video AND lang:en",count='30')
        else: # not first page
            results = twt.search(q="#"+hashtag+" AND url:news OR url:blog AND -url:bit AND -filter:retweets AND -filter:media AND -filter:native_video AND lang:en",include_entities='true',max_id=next_max_id)

        # remove unwanted substrings from tweet text
        for result in results['statuses']:
            finalResult = ["", "", []]
            tweet_text = result['text']
            tweet_text = tweet_text.replace("\n", "")
            tweet_text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", tweet_text)
            tweet_text = tweet_text.replace("https://", "")
            tweet_text = tweet_text.replace("http://", "")
            tweet_text = tweet_text.replace("https", "")
            tweet_text = tweet_text.replace("http", "")
            tweet_text = tweet_text.replace("  ", "")
            try:
                tweet_external_link = result['entities']['urls'][0]['expanded_url']
                if ("t.co" not in tweet_external_link) and ("twitter." not in tweet_external_link): # make sure 'tweet_external_link' is not an internal twitter link
                    finalResult[1] = tweet_external_link
                    
                    for dic in result['entities']['hashtags']:
                        finalResult[2].append(dic["text"])
                        
                    if not finalResult[2] == []: # check if tweet really contained hashtag (Twitter API bug?)
                        if not alreadyFoundURL(tweets, finalResult[1]): # check whether we already fetched this URL before
                            tweets.append(finalResult)
                    
            except:
                break # No URLs or other index error
                
        try:
            next_results_url_params = results['search_metadata']['next_results'] # get the url for the next results page
            next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
        except:
            break # no more 'next_results' exist
        
    return tweets



#       Conditions:                                                                         #
#                       - Tweet was posted from an English-speaking person                  #
#                       - Tweet includes the query Hashtag                                  #
#                       - Tweet includes an external URL to a news/blog article             #
#                       - All result URLs are unique                                        #
#                       -                                                                   #
#                                                                                           #
#       SOME LINKS don't show, because a tweet was posted "via" something                   #



#results = getData("apple", 30)
#print(len(results))
#for result in results:
#    print(result)

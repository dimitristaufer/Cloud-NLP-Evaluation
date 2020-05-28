import sys
sys.path.append('../')
sys.path.append('../..')
import time
import watson_nlp_calls as Watson
import google_cloud_nlp_calls as GoogleCloud
import azure_nlp_calls as Azure
import aws_nlp_calls as AWS

decimalPointsOffset = 4
decimalPointsTFC = 4

def makeCalls(text, stars):
    """
    Sends out sentiment analysis calls to all four providers using their SDKs, measures the time for completion, and calculates the resulting polarity offset.

    Arguments:
        text {String} -- Text to be analyzed.
        stars {Double} -- The star count of the Yelp review to be analyzed.

    Returns:
        Dictionary -- A dictionary containing all four provider's polarity offsets and their time for completion.
    """
    
    start = time.time()
    ibm = Watson.analyzeSentiment(text)
    end = time.time()
    ibmTFC = end-start  # in seconds

    start = time.time()
    google = GoogleCloud.analyzeSentiment(text)
    end = time.time()
    googleTFC = end-start  # in seconds

    start = time.time()
    microsoft = Azure.analyzeSentiment(text)
    end = time.time()
    microsoftTFC = end-start  # in seconds

    start = time.time()
    amazon = AWS.analyzeSentiment(text)
    end = time.time()
    amazonTFC = end-start  # in seconds

    ibmOffset = toYelpScore(float(ibm.value))-stars
    googleOffset = toYelpScore(float(google.value))-stars
    microsoftOffset = toYelpScore(microsoft.value)-stars
    amazonOffset = toYelpScore(amazon.value)-stars

    result = {"values": {'ibm': {'polarity_offsets': round(ibmOffset, decimalPointsOffset), 'time_for_completion': round(ibmTFC, decimalPointsTFC)},
                         'google': {'polarity_offsets': round(googleOffset, decimalPointsOffset), 'time_for_completion': round(googleTFC, decimalPointsTFC)},
                         'microsoft': {'polarity_offsets': round(microsoftOffset, decimalPointsOffset), 'time_for_completion': round(microsoftTFC, decimalPointsTFC)},
                         'amazon': {'polarity_offsets': round(amazonOffset, decimalPointsOffset), 'time_for_completion': round(amazonTFC, decimalPointsTFC)}},
              "errors": {'ibm': ibm.errorMessage,
                         'google': google.errorMessage,
                         'microsoft': microsoft.errorMessage,
                         'amazon': amazon.errorMessage}}

    return result

def toYelpScore(sentiment):
    """
    Transforms a normalized sentiment analysis polarity rating to the Yelp 5 star format.

    Arguments:
        sentiment {Double} -- Polarity rating.

    Returns:
        Double -- Transformed polarity rating.
    """
    return (sentiment*4)+1

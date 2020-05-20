import sys
sys.path.append('../..')
import time
import watson_nlp_calls as Watson
import google_cloud_nlp_calls as GoogleCloud
import aws_nlp_calls as AWS

decimalPointsTFC = 4

def makeCalls(text):
    """
    Sends out syntax analysis calls to three providers using their SDKs, and measures the time for completion.

    Arguments:
        text {String} -- Text to be analyzed.

    Returns:
        Dictionary -- A dictionary containing all three provider's values and their time for completion.
    """
    
    start = time.clock()
    ibm = Watson.analyzeSyntax(text)
    end = time.clock()
    ibmTFC = end-start  # in seconds

    start = time.clock()
    google = GoogleCloud.analyzeSyntax(text)
    end = time.clock()
    googleTFC = end-start  # in seconds

    start = time.clock()
    amazon = AWS.analyzeSyntax(text)
    end = time.clock()
    amazonTFC = end-start  # in seconds

    result = {"values": {'ibm': {'tokens': ibm.values, 'time_for_completion': round(ibmTFC, decimalPointsTFC)},
                         'google': {'tokens': google.values, 'time_for_completion': round(googleTFC, decimalPointsTFC)},
                         'amazon': {'tokens': amazon.values, 'time_for_completion': round(amazonTFC, decimalPointsTFC)}},
              "errors": {'ibm': ibm.errorMessage,
                         'google': google.errorMessage,
                         'amazon': amazon.errorMessage}}

    return result

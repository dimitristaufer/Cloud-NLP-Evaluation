import sys
sys.path.append('../..')
import time
import watson_nlp_calls as Watson
import google_cloud_nlp_calls as GoogleCloud
import azure_nlp_calls as Azure
import aws_nlp_calls as AWS

decimalPointsTFC = 4

def makeCalls(text):
    """
    Sends out entity recognition calls to all four providers using their SDKs, and measures the time for completion.

    Arguments:
        text {String} -- Text to be analyzed.

    Returns:
        Dictionary -- A dictionary containing all four provider's results and their time for completion.
    """
    
    start = time.clock()
    ibm = Watson.analyzeEntities(text)
    end = time.clock()
    ibmTFC = end-start  # in seconds

    start = time.clock()
    google = GoogleCloud.analyzeEntities(text)
    end = time.clock()
    googleTFC = end-start  # in seconds

    start = time.clock()
    microsoft = Azure.analyzeEntities(text)
    end = time.clock()
    microsoftTFC = end-start  # in seconds

    start = time.clock()
    amazon = AWS.analyzeEntities(text)
    end = time.clock()
    amazonTFC = end-start  # in seconds

    result = {"values": {'ibm': {'entities': ibm.values, 'time_for_completion': round(ibmTFC, decimalPointsTFC)},
                         'google': {'entities': google.values, 'time_for_completion': round(googleTFC, decimalPointsTFC)},
                         'microsoft': {'entities': microsoft.values, 'time_for_completion': round(microsoftTFC, decimalPointsTFC)},
                         'amazon': {'entities': amazon.values, 'time_for_completion': round(amazonTFC, decimalPointsTFC)}},
              "errors": {'ibm': ibm.errorMessage,
                         'google': google.errorMessage,
                         'microsoft': microsoft.errorMessage,
                         'amazon': amazon.errorMessage}}

    return result

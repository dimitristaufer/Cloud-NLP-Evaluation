import sys
sys.path.append('../..')
import time
import watson_nlp_calls as Watson
import google_cloud_nlp_calls as GoogleCloud

decimalPointsTFC = 4

def googleMakeCall(text):
    """
    Sends out a content classifications call to Google Cloud using their SDKs, and measures the time for completion.

    Arguments:
        text {String} -- Text to be analyzed.

    Returns:
        Dictionary -- A dictionary containing the results and the time for completion.
    """
    
    start = time.time()
    google = GoogleCloud.classifyContent(text)
    end = time.time()
    googleTFC = end-start  # in seconds
    
    # e.g. [{'category': '/Arts & Entertainment/Visual Art & Design/Photographic & Digital Arts', 'confidence': 0.949999988079071}, {'category': '/Computers & Electronics/Consumer Electronics/Camera & Photo Equipment', 'confidence': 0.9399999976158142}, {'category': '/Hobbies & Leisure', 'confidence': 0.9200000166893005}]
    result = {
        "categories" : google.values,
        "time_for_completion" : round(googleTFC, decimalPointsTFC),
        "errors" : google.errorMessage
    }
    return result
    
def ibmMakeCall(text):
    """
    Sends out a content classifications call to IBM Cloud using their SDKs, and measures the time for completion.

    Arguments:
        text {String} -- Text to be analyzed.

    Returns:
        Dictionary -- A dictionary containing the results and the time for completion.
    """
    
    start = time.time()
    ibm = Watson.classifyContent(text)
    end = time.time()
    ibmTFC = end-start  # in seconds
    
    # e.g. [{'category': '/technology and computing/consumer electronics/camera and photo equipment/cameras and camcorders/cameras', 'confidence': 0.999672}, {'category': '/technology and computing/consumer electronics/camera and photo equipment/cameras and camcorders/camera bags', 'confidence': 0.983271}, {'category': '/technology and computing/consumer electronics/camera and photo equipment/cameras and camcorders/camera batteries', 'confidence': 0.973341}]
    result = {
        "categories" : ibm.values,
        "time_for_completion" : round(ibmTFC, decimalPointsTFC),
        "errors" : ibm.errorMessage
    }
    return result

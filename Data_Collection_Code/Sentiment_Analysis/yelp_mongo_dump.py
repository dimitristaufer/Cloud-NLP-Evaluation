import sys
sys.path.append('../')
sys.path.append('../..')
from datetime import datetime
import itertools
import json
from mongo_connect import Connect

def import_yelp_dataset():
    """
    Formats and imports the Yelp Open Dataset from a local json file into a local Mongo DB database.
    """
    ### Mongo DB Init ###
    connection = Connect.get_connection()

    db = connection.sentimentAnalysis
    allYelpReviews = db.allYelpReviews
    ###               ###

    filename = "../../External_Datasets/yelp_dataset/review.json"
    # 6.685.900 reviews

    print("running... it takes approx 37 minutes for all.")
    f = open(filename)
    for line in itertools.islice(f, 0, 2000):
        line = line.strip()
        if not line:
            continue
        review = json.loads(line)
        now = datetime.now()
        dateString = now.strftime("%d-%m-%Y %H:%M:%S")
        allYelpReviews.insert_one({"review_id": review['review_id'], "reviewDate": review['date'], "addedDate": dateString,
                                   "stars": review['stars'], "text": review['text'], "usefulness": review['useful'], "characterCount": len(review['text'])})

    f.close()

# Usage Example:

#import_yelp_dataset()

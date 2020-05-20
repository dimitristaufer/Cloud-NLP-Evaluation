from pymongo import MongoClient

class Connect(object):
    """
    Establishes a connection with a local MongoDB database.

    Arguments:
        object {None} -- None

    Returns:
        MongoClient -- A MongoClient to use to connect and perform operations
    """
    
    @staticmethod
    def get_connection():
        """
        Establishes a connection with a local MongoDB database.

        Returns:
            MongoClient -- A MongoClient to use to connect and perform operations
        """
        return MongoClient("mongodb://username:password@localhost:27017")

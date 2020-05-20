import spacy
import neuralcoref

def coRefs(text):
    """
    Calculates the coreferences in a text using Spacy's en_core_web_lg large English model.
    
    Returns:
        Dictionary -- The total amount of clusters, mentions, the values, and our calculated difficulty value
    """
    # https://spacy.io/models/en
    nlp = spacy.load('en_core_web_lg') # Large English Model (685k keys, 685k unique vectors (300 dimensions))
    #nlp = spacy.load('en')
    neuralcoref.add_to_pipe(nlp)

    doc = nlp(text)
    #print(doc._.has_coref)
    #print(doc._.coref_resolved)
    clusters = doc._.coref_clusters

    totalClusters = len(clusters)
    totalMentions = 0
    clusterStrings = []

    for cluster in clusters:
        clusterStrings.append(repr(cluster.mentions))
        totalMentions += len(cluster)
    difficulty = totalClusters + totalMentions # high equals more difficult
    clusterStringsString = ','.join(clusterStrings)
    
    return {"totalClusters" : totalClusters,
            "totalMentions" : totalMentions,
            "values" : clusterStringsString,
            "difficulty" : difficulty}

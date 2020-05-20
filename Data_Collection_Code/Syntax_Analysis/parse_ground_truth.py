import sys
sys.path.append('../')
sys.path.append('../..')
import pyconll
from mongo_connect import Connect

# This program parses two POS corpora and stores them in a local mongoDB database #

### Universal Dependencies version of syntax annotations
#   from the GUM corpus (https://corpling.uis.georgetown.edu/gum/) ###
                                                              
### 5.427 sentences, 101.277 Tokens                                ###
### Copyright: CC BY-NC-SA 4.0                                     ###
### https://universaldependencies.org                              ###


### Noun Verb Dataset by Elkahky et al. (https://www.aclweb.org/anthology/D18-1277.pdf)         ###

### @InProceedings{NOUNVERB,                                                                    ###
###                title = {A Challenge Set and Methods for Noun-Verb Ambiguity},               ###
###                author = {Ali Elkahky and Kellie Webster and Daniel Andor and Emily Pitler}, ###
###                booktitle = {Proceedings of EMNLP},                                          ###
###                year = {2018}                                                                ###
###                }                                                                            ###
###                                                                                             ###



### Mongo DB Init ###
connection = Connect.get_connection()

db = connection.syntaxAnalysis
udGroundTruth = db.udGroundTruth
udGroundTruthCopy = db.udGroundTruthCopy
udPTGroundTruth = db.udPTGroundTruth
udPTGroundTruthCopy = db.udPTGroundTruthCopy
udEWGroundTruth = db.udEWGroundTruth
udEWGroundTruthCopy = db.udEWGroundTruthCopy

nvGroundTruth = db.nvGroundTruth
nvGroundTruthCopy = db.nvGroundTruthCopy
###               ###

UD_EN_DEV = '../../../External_Datasets/Syntax_Analysis/UD_English-GUM-master/en_gum-ud-dev.conllu' # 0.9 MB
UD_EN_TEST = '../../../External_Datasets/Syntax_Analysis/UD_English-GUM-master/en_gum-ud-test.conllu' # 0.9 MB
UD_EN_TRAIN = '../../../External_Datasets/Syntax_Analysis/UD_English-GUM-master/en_gum-ud-train.conllu' # 4.0 MB

UD_PT_EN_DEV = '../../../External_Datasets/Syntax_Analysis/UD_English-ParTUT-master/en_partut-ud-dev.conllu' # 0.2 MB
UD_PT_EN_TEST = '../../../External_Datasets/Syntax_Analysis/UD_English-ParTUT-master/en_partut-ud-test.conllu' # 0.2 MB
UD_PT_EN_TRAIN = '../../../External_Datasets/Syntax_Analysis/UD_English-ParTUT-master/en_partut-ud-train.conllu' # 2.4 MB

UD_EW_EN_DEV = '../../../External_Datasets/Syntax_Analysis/UD_English-EWT-master/en_ewt-ud-dev.conllu' # 1.7 MB
UD_EW_EN_TEST = '../../../External_Datasets/Syntax_Analysis/UD_English-EWT-master/en_ewt-ud-test.conllu' # 1.7 MB
UD_EW_EN_TRAIN = '../../../External_Datasets/Syntax_Analysis/UD_English-EWT-master/en_ewt-ud-train.conllu' # 13.3 MB

'''
ADJ: adjective
ADP: adposition
ADV: adverb
AUX: auxiliary
CCONJ: coordinating conjunction
DET: determiner
INTJ: interjection
NOUN: noun
NUM: numeral
PART: particle
PRON: pronoun
PROPN: proper noun
PUNCT: punctuation
SCONJ: subordinating conjunction
SYM: symbol
VERB: verb
X: other
'''

NV_EN_DEV = '../../../External_Datasets/Syntax_Analysis/noun-verb-master/dev.conll' # 1.2 MB
NV_EN_TEST = '../../../External_Datasets/Syntax_Analysis/noun-verb-master/test.conll' # 3.0 MB
NV_EN_TRAIN = '../../../External_Datasets/Syntax_Analysis/noun-verb-master/train.conll' # 10.6 MB

'''
VERB
NON-VERB
'''

def getTestDataUDDev():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_EN_DEV)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udGroundTruth.insert_one(groundTruthDocument)
        udGroundTruthCopy.insert_one(groundTruthDocument)     

def getTestDataUDTest():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_EN_TEST)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udGroundTruth.insert_one(groundTruthDocument)
        udGroundTruthCopy.insert_one(groundTruthDocument)  
        
def getTestDataUDTrain():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_EN_TRAIN)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udGroundTruth.insert_one(groundTruthDocument)
        udGroundTruthCopy.insert_one(groundTruthDocument) 

def getTestDataNVDev():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(NV_EN_DEV)
    for sentence in devSet:
        sentenceText = ""
        groundTruthDocument = {}
        for i, token in enumerate(sentence):
            if i == len(sentence)-1:
                sentenceText += token.form + ""
            else:
                sentenceText += token.form + " "
            if token.upos == "VERB":
                groundTruthDocument["annotation"] = {
                    "token_text" : token.form,
                    "pos_tag" : "VERB"
                }
            elif token.upos == "NON-VERB":
                groundTruthDocument["annotation"] = {
                    "token_text" : token.form,
                    "pos_tag" : "NON-VERB"
                }
        groundTruthDocument["sentence"] = sentenceText
        nvGroundTruth.insert_one(groundTruthDocument)
        nvGroundTruthCopy.insert_one(groundTruthDocument)

def getTestDataNVTest():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(NV_EN_TEST)
    for sentence in devSet:
        sentenceText = ""
        groundTruthDocument = {}
        for i, token in enumerate(sentence):
            if i == len(sentence)-1:
                sentenceText += token.form + ""
            else:
                sentenceText += token.form + " "
            if token.upos == "VERB":
                groundTruthDocument["annotation"] = {
                    "token_text" : token.form,
                    "pos_tag" : "VERB"
                }
            elif token.upos == "NON-VERB":
                groundTruthDocument["annotation"] = {
                    "token_text" : token.form,
                    "pos_tag" : "NON-VERB"
                }
        groundTruthDocument["sentence"] = sentenceText
        nvGroundTruth.insert_one(groundTruthDocument)
        nvGroundTruthCopy.insert_one(groundTruthDocument)

def getTestDataUDPTDev():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_PT_EN_DEV)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udPTGroundTruth.insert_one(groundTruthDocument)
        udPTGroundTruthCopy.insert_one(groundTruthDocument) 
        
def getTestDataUDPTTest():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_PT_EN_TEST)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udPTGroundTruth.insert_one(groundTruthDocument)
        udPTGroundTruthCopy.insert_one(groundTruthDocument) 
        
def getTestDataUDPTTrain():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_PT_EN_TRAIN)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udPTGroundTruth.insert_one(groundTruthDocument)
        udPTGroundTruthCopy.insert_one(groundTruthDocument) 
        
def getTestDataUDEWDev():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_EW_EN_DEV)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udEWGroundTruth.insert_one(groundTruthDocument)
        udEWGroundTruthCopy.insert_one(groundTruthDocument)
        
def getTestDataUDEWTest():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_EW_EN_TEST)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udEWGroundTruth.insert_one(groundTruthDocument)
        udEWGroundTruthCopy.insert_one(groundTruthDocument)
        
def getTestDataUDEWTrain():
    """
    Imports conll type ground-truth data into a local MongoDB for POS-tagging testing.
    """
    devSet = pyconll.load_from_file(UD_EW_EN_TRAIN)
    for sentence in devSet:
        groundTruthDocument = {
            "sentence" : sentence.text
        }
        posTags = []
        index = 0
        for token in sentence:
            posTags.append({
                "token_text" : token.form,
                "token_begin_offset" : index,
                "pos_tag" : token.upos
            })
            
            index += (len(token.form)+1)
        groundTruthDocument['annotation'] = posTags    
        udEWGroundTruth.insert_one(groundTruthDocument)
        udEWGroundTruthCopy.insert_one(groundTruthDocument) 

# Usage Example:

getTestDataUDDev()
getTestDataUDTest()
getTestDataUDTrain()

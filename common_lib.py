import nltk
from nltk.corpus import wordnet as wn
from nltk.parse import stanford
from nltk.internals import find_jars_within_path
from nltk.corpus import stopwords
import re
from nltk.tag.stanford import StanfordNERTagger

def buildSynset(word, pos, hyponyms=True, hypernyms=True):
    """ Input: a word from the query string and its part of speech.
    Output: list of words
    Returns the synset of the given word. Optionally
    returns the hyopnyms and hypernyms of a word. """
    try:
        syn = wn.synsets(word, pos=pos)
    except KeyError:
        print "not in synsets"
        return []
    # Build list of words from synsets, hyponyms and hypernyms
    synonyms = []
    for lemma in syn:
        word = lemma.name().split(".")[0]
        if not word in synonyms:
            synonyms.append(word)
        if hyponyms:
            synonyms = addCategory(synonyms, lemma)
        if hypernyms:
            synonyms = addCategory(synonyms, lemma, hyponym=False)
        synonyms = editSpaces(synonyms)
    return synonyms

def buildFullQuery(subject, content, parser, stop, hyponyms=False, hypernyms=False):
    if(subject in content):
        query = content
    elif(content in subject):
        query = subject
    else:
        query = subject + " " + content
    # Regular expression that takes everything in the parentheses and removes it
    query = re.sub(r'\([^)]*\)', '', query)
    importantTags = ["JJ", "NNP", "NN", "VBN", "VB", "NNS", "CD"]
    query.replace('!', '.')
    query.replace('?', '.')
    queryseparated = query.split('. ')
    queryParts = []


    for query_part in queryseparated:
        if len(query_part) < 3:
            continue
        imp = importantWords(query_part, parser)
        token = nltk.word_tokenize(query_part)
        posTags = nltk.pos_tag(token)
        # Find "important" tags and get synsets
        synsets = []
        for (word, tag) in posTags:
            #print word, tag
            if tag in importantTags or word == imp and not(word in stop):
                t = None
                if tag == "JJ":
                    t = wn.ADJ
                elif tag == "NNP" or tag == "NN":
                    t = wn.NOUN
                elif tag == "VBN":
                    t = wn.VERB
                elif tag == "VB":
                    t = wn.VERB
                # Find synset of word:
                if t:
                    synset = buildSynset(word, t, hyponyms, hypernyms)
                else:
                    synset = [word]
                if len(synset) == 0:
                    synset = [word]
                if len(synset) != 0:
                    if(len(synset)>=3):
                        synset = synset[0:3]
                    queryParts.append("(" + " OR ".join(synset) + ")")

    # function set removes duplicates and function list converts the set into list
    queryParts = list(set(queryParts))
    if len(queryParts) != 0:
        expansion =  " AND ".join(queryParts)
    else:
        expansion = ""
    return expansion

def addCategory(synList, lemma, hyponym=True):
    """ Add all hyponyms or hypernyms to synList """
    if hyponym:
        nymList = lemma.hyponyms()
    else:
        nymList = lemma.hypernyms()
    for hypo in nymList:
        n = hypo.name
        word = n().split(".")[0]
        if not word in synList:
            synList.append(word)
    return synList

def editSpaces(words):
    newWords = []
    for w in words:
        if "_" in w:
            w = '\"' + w.replace("_", " ") + '\"'
        newWords.append(w)
    return newWords

def importantWords(sentence, parser):
    result = parser.raw_parse(sentence)
    dep = result.next()
    return list(dep.triples())[0][0][0]

def Tokenize(text):
    return nltk.word_tokenize(text)

def Init():
    parser = stanford.StanfordDependencyParser(model_path="./stanford_libs/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    stanford_dir = parser._classpath[0].rpartition('/')[0]
    stanford_jars = find_jars_within_path(stanford_dir)
    parser._classpath = tuple(find_jars_within_path(stanford_dir))

    st = StanfordNERTagger('./stanford_libs/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz',
    './stanford_libs/stanford-ner-2015-12-09/stanford-ner.jar')
    stanford_dir = st._stanford_jar.rpartition('/')[0]
    st._stanford_jar = ':'.join(find_jars_within_path(stanford_dir))

    stop = stopwords.words('english')
    return parser, st, stop

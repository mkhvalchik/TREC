import html2text
import urllib2
import math
import common_lib
import re
import nltk, string
import machine_learning
import socket
from sklearn.feature_extraction.text import TfidfVectorizer
from langdetect import detect

# Returns text from the url.
def GetTextFromLink(link):
    if link.find(".pdf") != -1:
        return None
    try:
        req = urllib2.Request(link, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = urllib2.urlopen(req, timeout=2.5).read()
    except urllib2.URLError:
        return None
    except socket.timeout:
        return None
    try:
        html = unicode(html, 'utf-8')
    except:
        return None
    if link.find("answers.yahoo") != -1:
        pos = html.find('Best Answer')
        if (pos != -1):
            html = html[pos:]
        else:
            html = ""
    # print html
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    try:
        text = unicode(h.handle(html))
    except:
        return ""
    return text

# For a given text, returns allcominations of 3 nearby sentences
def GetAllPassages(keywords, text):
    # these chracters break the string in sentences
    sentences = re.split('[!\.\?\n] ', text)
    if len(sentences) < 4:
        return None
    j = 4
    passages = []
    for i in range(len(sentences) - 3):
        passages.append(sentences[i:j])
        j += 1
    filtered_passages = []
    stemmed_keywords = stem_tokens(SplitKeywords(keywords))
    # doing filtering to remove small passages
    for passage in passages:
        too_short = False
        for part in passage:
            if len(part) < 6 or len(part.split(' ')) < 4:
                too_short = True
                break
        if too_short:
            continue
        words = ' '.join(passage).lower()
        if (words.count("  * ") > 1):
            continue
        if (words.count('\n\n') >= 2):
            continue
        if (words.find('###') != -1):
            continue
        if (words.count('*') >= 10 or words.count('|') >= 10):
            continue
        if (words.find('.jpg') != -1 or words.find('.JPG') != -1):
            continue
        if words.find("---") != -1:
            continue
        if (len(words) < 40):
            continue
        if (len(words.split(' ')) < 10):
            continue
        # Filter out words which don't contain any of the keywords
        found = False
        for keyword in stemmed_keywords:
            if words.find(keyword.lower()) != -1:
                found = True
                break
        if not found:
            continue
        filtered_passage = '. '.join(passage)
        filtered_passage = filtered_passage.replace("**", "")

        filtered_passages.append(filtered_passage)
    return filtered_passages

# Compute IDFs from the given query and list of passages.
def ComputeIDFsAndAvgl(keywords, documents):
    idfs = {}
    sum_len = 0
    search_terms = SplitKeywords(keywords)
    stemmed_keywords = [w.lower() for w in stem_tokens(search_terms)]
    # iterate over all passages
    for doc in documents:
        sum_len += len(doc)
        doc = stem_tokens(common_lib.Tokenize(doc))
        for search_term in list(set(stemmed_keywords)):
            found = False
            for d in doc:
                if search_term.lower() == d.lower():
                    if search_term in idfs:
                        idfs[search_term] += 1
                    else:
                        idfs[search_term] = 1
                    found = True
                    break
            if found:
                continue
    idfs_return = {}
    # Computing IDF formula
    for key in idfs:
        idfs_return[key] =  math.log(float(len(documents))/idfs[key], 2)
    return idfs_return, float(sum_len) / len(documents)

# Compute score for a given passage and query. Avgl - average doc length.
def ComputeBM25(keywords, idfs, passage, avgl):
    tokens = stem_tokens(common_lib.Tokenize(passage.lower()))
    #print tokens
    score = 0
    search_terms = SplitKeywords(keywords)
    stemmed_keywords = stem_tokens(search_terms)
    for search_term in stemmed_keywords:
        raw_freq = tokens.count(search_term.lower())
        if (raw_freq == 0):
            freq = 0
        else:
            freq = 1 + math.log(raw_freq, 2)
        idf = 0
        if search_term.lower() in idfs:
            idf = idfs[search_term.lower()]
        score += float(idf) * (freq * (2 + 1)) / (freq + 2 * (1 - 0.75 + 0.75 * len(passage)/avgl))
    return score

# Gets top passage from the list of passages.
def GetTopPassageFromList(keywords, passages):
    idfs, avgl = ComputeIDFsAndAvgl(keywords, passages)
    top_passage = ''
    top_score = -1
    for passage in passages:
        score = ComputeBM25(keywords, idfs, passage, avgl)
        #print str(score) + " " + passage.encode('utf-8')
        if (score >= top_score):
            top_score = score
            top_passage = passage
    try:
        if detect(top_passage) != 'en':
            return None, None
    except:
        return None, None
    return top_passage, top_score

# Gets top passage from the list of passages with using of ML model.
def GetTopPassageFromLinkWithML(keywords, link):
    text = GetTextFromLink(link)
    if not text:
        return None, None
    passages = GetAllPassages(keywords, text)
    if not passages:
        return None, None
    idfs, avgl = ComputeIDFsAndAvgl(keywords, passages)
    top_passage = ''
    top_score = -1
    results = []
    for passage in passages:
        score = ComputeBM25(keywords, idfs, passage, avgl)
        results.append([passage, score, 1.0])

    results.sort(key=lambda tup: tup[1], reverse=True)
    X, Y = machine_learning.ComputePassageFeatures(keywords, results)
    model = machine_learning.LoadModel("passages.model")

    # predicting the labels
    Y = []
    for x in X:
        Y.append(machine_learning.Predict(model, x)[0])

    # candidate answers
    candidates = []

    # sometimes none of the candidates is classified as 1, in this case we need to
    # add all candidates.
    add_all = True
    for y in Y:
        if y == 1:
            add_all = False

    for i in range(len(Y)):
        if Y[i] == 1 or add_all:
            # X[i][0] is a BM25 rank of passage
            candidates.append(results[X[i][0] - 1])

    for candidate in candidates:
        if candidate[1] > top_score:
            top_score = candidate[1]
            top_passage = candidate[0]

    if len(top_passage) <= 0:
        return None, None

    top_passage = RemoveParenthesis(top_passage)
    try:
        if detect(top_passage) != 'en':
            return None, None
    except:
        return None, None

    return top_passage, top_score

# removes all text between brackets.
def RemoveParenthesis(text):
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in text:
        if i == '[':
            skip1c += 1
        elif i == '(':
            skip2c += 1
        elif i == ']' and skip1c > 0:
            skip1c -= 1
        elif i == ')'and skip2c > 0:
            skip2c -= 1
        elif skip1c == 0 and skip2c == 0:
            ret += i
    return ret

# Score passages from the list
def ScorePassages(keywords, passages):
    if not passages:
        return None
    idfs, avgl = ComputeIDFsAndAvgl(keywords, passages)
    top_passage = ''
    top_score = -1
    ret = []
    for passage in passages:
        score = ComputeBM25(keywords, idfs, passage, avgl)
        ret.append([passage, score])
    return ret

# Get top passage per link
def GetTopPassage(keywords, text):
    if not text:
        return None, None
    passages = GetAllPassages(keywords, text)
    if not passages:
      return None, None
    return GetTopPassageFromList(keywords, passages)

# Get top passage per link
def GetTopPassageFromLink(keywords, link):
    return GetTopPassage(keywords, GetTextFromLink(link))

# Get list of pairs: passage and bm25 score
def GetScoredPassages(keywords, link):
    text = GetTextFromLink(link)
    if not text:
        return None
    passages = GetAllPassages(keywords, text)
    if not passages:
        return None
    return ScorePassages(keywords, passages)

# Splits keyworded query into keywords
def SplitKeywords(keywords):
    out = []
    for keyword in keywords.split(" AND "):
        keyword = keyword.replace("(", "")
        keyword = keyword.replace(")", "")
        for search_term in keyword.split(" OR "):
            search_term = search_term.replace("\"", "")
            out.append(search_term)
    return out

# Removes synonyms from the keywords
def RemoveSynonymsFromKeywords(keywords):
    splitted_keywords = keywords.split(" AND ")
    filtered_keywords = [keyword.split(" OR ")[0].replace("(", "").replace(")", "") for keyword in splitted_keywords]
    filtered_keywords_ret = []
    for keyword in filtered_keywords:
        if not (keyword.lower() in ["what", "how", "why", "where", "when", "which"]):
            filtered_keywords_ret.append(keyword)
    return " AND ".join(filtered_keywords_ret)

# Compute number of keywords in a given passage.
def ScorePassage(keywords, passage):
    tokens = common_lib.Tokenize(passage)
    score = 0
    search_terms = SplitKeywords(keywords)
    for search_term in search_terms:
        score += tokens.count(search_term)
    return score

def stem_tokens(tokens):
    stemmer = nltk.stem.porter.PorterStemmer()
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

# Get similarity between two texts
def GetSimilarity(text1, text2):
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

#keywords = "(hamburger OR \"ground beef\") AND (cold) AND (heat OR inflame) AND (What) AND (manner OR means OR direction)"
#print GetTopPassageFromLink(keywords, 'http://hyperphysics.phy-astr.gsu.edu/hbase/thermo/refrig.html')
#passage, score = GetTopPassage(keywords,
#                    GetTextFromLink('http://www.livestrong.com/article/480524-how-to-reheat-hamburgers/'))

#print passage, score
#print ScorePassage(keywords, passage)

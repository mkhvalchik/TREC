import html2text
import urllib2
import math
import common_lib
import re
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

# Returns text from the url.
def GetTextFromLink(link):
    if link.find(".pdf") != -1:
        return None
    try:
        req = urllib2.Request(link, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = unicode(urllib2.urlopen(req, timeout=1.5).read(), 'utf-8')
    except:
        return None
    #print html
    h = html2text.HTML2Text()
    h.ignore_links = True
    return unicode(h.handle(html))

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
        filtered_passage = re.sub(r'\([^)]*\)', '', filtered_passage)
        filtered_passage = re.sub(r'\[[^[]]*\]', '', filtered_passage)
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
    return top_passage, top_score

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

#!/usr/bin/python
import pprint
import xml.etree.ElementTree
from HTMLParser import HTMLParser
from googleapiclient.discovery import build
import common_lib
import passage_retrieval
import machine_learning
from py_bing_search import PyBingSearch
from py_bing_search import PyBingException
import sys
import warnings
import string
import signal

warnings.filterwarnings("ignore")

def signal_handler(signum, frame):
    raise Exception("Timed out!")

# Get top 20 search result links for a given query using Bing
def GetLinksForQueryBing(query):
    bing = PyBingSearch('3Bybyj2qcK/w5FXbBqBUjI9MajN51efC2uYldmzvvnY')
    try:
        result_list = bing.search_all(query, limit=20, format='json')
    except PyBingException:
        return []
    results = [result.url for result in result_list]
    results = results[:min(20, len(results))]
    return [r for r in results if r.find("youtube") == -1]

# Get top 20 search result links for a given query using Google
def GetLinksForQueryGoogle(query):
    service = build("customsearch", "v1",
          developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

    res = service.cse().list(
        q=query,
        cx='000504779742960611072:dpmv5fihhu8',
      ).execute()

    results = [item['link'] for item in res['items']]
    results = results[:min(20, len(results))]
    return [r for r in results if r.find("youtube") == -1]

parser, st, stop = common_lib.Init()

title = sys.argv[1]
body = sys.argv[1]

signal.signal(signal.SIGALRM, signal_handler)
signal.alarm(51)   # 51 seconds

try:
    keyword_query = common_lib.buildFullQuery(title, body, parser, stop)

    links_bing_yahoo = GetLinksForQueryBing("answers.yahoo.com " + keyword_query)[:2]
    links_bing = links_bing_yahoo + GetLinksForQueryBing(keyword_query)
    links_google = GetLinksForQueryGoogle(keyword_query)

    keyword_query =  passage_retrieval.RemoveSynonymsFromKeywords(keyword_query)

    sum_score = 0
    len_score = 0
    results = []
    rank = 1
    for link in links_bing:
        passage, score = passage_retrieval.GetTopPassageFromLinkWithML(keyword_query, link)
        if passage:
            results.append([link, link in links_google, passage, 0, rank])
        rank += 1
except:
    i = 1

X, _ = machine_learning.ComputeAnswerFeatures(keyword_query, results)
model = machine_learning.LoadModel("answers.model")

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
        # X[i][0] is bing rank of passage
        for result in results:
            if result[4] == X[i][1]:
                candidates.append(result[2])

# Next, we selecting the top passage out of all BM25 candidates
scored_passages = passage_retrieval.ScorePassages(keyword_query, candidates)
max_bm25_score = -1
top_passage = ""
for s in scored_passages:
    if s[1] > max_bm25_score:
        max_bm25_score = s[1]
        top_passage = s[0]

top_passage = filter(lambda x: x in string.printable, top_passage)

unescape = HTMLParser().unescape
print unescape(top_passage.replace("\n", " ").replace("  ", " ").replace("  ", " ").encode('utf-8'))

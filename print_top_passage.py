import pprint
import xml.etree.ElementTree
from xml.sax.saxutils import escape
from googleapiclient.discovery import build
import common_lib
import passage_retrieval
from py_bing_search import PyBingSearch
import sys

# Get top 10 search result links for a given query
def GetLinksForQuery(query):
    bing = PyBingSearch('3Bybyj2qcK/w5FXbBqBUjI9MajN51efC2uYldmzvvnY')
    result_list = bing.search_all(query, limit=20, format='json')

    return [result.url for result in result_list][:20]

parser, st, stop = common_lib.Init()

title = sys.argv[1]
body = sys.argv[2]

keyword_query = common_lib.buildFullQuery(title, body, parser, stop)

links = GetLinksForQuery(keyword_query)

sum_score = 0
len_score = 0
passages = []

for link in links:
    print "link"
    passage, _ = passage_retrieval.GetTopPassageFromLink(keyword_query, link)
    if passage:
        passages.append(passage)

top_passage = passage_retrieval.GetTopPassageFromList(keyword_query, passages)

print top_passage[0]

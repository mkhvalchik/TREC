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

query = sys.argv[1]

keyword_query = common_lib.buildFullQuery(query, query, parser, stop)

links_keywords = GetLinksForQuery([keyword_query])

sum_score = 0
len_score = 0

for link in links_keywords:
    passage, _ = passage_retrieval.GetTopPassageFromLink(keyword_query, link)
    if passage:
        score = passage_retrieval.ScorePassage(keyword_query, passage)
        sum_score += score
        len_score += 1
        print "======================================================"
        print passage.encode('utf-8')
        print "score ----------> " + str(score)
if (sum_score > 0):
    print "avg score ----------> " + str(float(sum_score) / len_score)

"""
service = build("customsearch", "v1",
        developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

res = service.cse().list(
  q='lectures',
  cx='000504779742960611072:dpmv5fihhu8',
).execute()
pprint.pprint(res)

print [item['link'] for item in res['items']]
"""

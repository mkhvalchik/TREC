import pprint
import xml.etree.ElementTree
from xml.sax.saxutils import escape
from googleapiclient.discovery import build
import common_lib
import passage_retrieval
import sys

# Get top 10 search result links for a given query
def GetLinksForQuery(query):
    service = build("customsearch", "v1",
            developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

    res = service.cse().list(
      q=query,
      cx='000504779742960611072:dpmv5fihhu8',
    ).execute()

    return [item['link'] for item in res['items']][:10]

# Returns a list of links appearing in search for a given request.
def GetLinksForQueries(queries):
    links = []
    for query in queries:
        links += GetLinksForQuery(query)
    # remove duplicates
    return list(set(links))


parser, st, stop = common_lib.Init()

query = sys.argv[1]

keyword_query = common_lib.buildFullQuery(query, query, parser, stop)

links_keywords = GetLinksForQueries([keyword_query])

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

import pprint
import xml.etree.ElementTree
from xml.sax.saxutils import escape
from googleapiclient.discovery import build
import common_lib
import passage_retrieval
from py_bing_search import PyBingSearch
import sys
import json

# Get top 10 search result links for a given query
def GetLinksForQueryGoogle(query):
    service = build("customsearch", "v1",
              developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

    res = service.cse().list(
        q=query,
        cx='000504779742960611072:dpmv5fihhu8',
      ).execute()

    return [item['link'] for item in res['items']][:20]

def GetLinksForQueryBing(query):
    bing = PyBingSearch('3Bybyj2qcK/w5FXbBqBUjI9MajN51efC2uYldmzvvnY')
    result_list = bing.search_all(query, limit=20, format='json')

    return [result.url for result in result_list][:20]

parser, st, stop = common_lib.Init()
output = {}
#f = open("links_results", "wb")
#f.write("<data>\n")
e = xml.etree.ElementTree.parse('small_sample.xml').getroot()
i = 0
for ves in e.findall('vespaadd'):
    for doc in ves.findall('document'):
        # adding links for keyword query
        print "next doc"
        keyword_query = common_lib.buildFullQuery(doc.find('subject').text, doc.find('content').text, parser, stop)
        google_links = GetLinksForQueryGoogle(keyword_query)
        bing_links = GetLinksForQueryBing(keyword_query)

        links = [google_links, bing_links]
        output[i] = links
        i += 1

with open('output_links.txt', 'w') as f:
  json.dump(output, f, ensure_ascii=False)

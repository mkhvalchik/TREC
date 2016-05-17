import pprint
import xml.etree.ElementTree
from xml.sax.saxutils import escape
from googleapiclient.discovery import build
import common_lib
import passage_retrieval
from py_bing_search import PyBingSearch
import sys
import json

# Get top 20 search result links for a given query using Bing
def GetLinksForQueryBing(query):
    #service = build("customsearch", "v1",
    #          developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

    #res = service.cse().list(
    #    q=query,
    #    cx='000504779742960611072:dpmv5fihhu8',
    #  ).execute()

    #return [item['link'] for item in res['items']][:20]

    try:
        bing = PyBingSearch('3Bybyj2qcK/w5FXbBqBUjI9MajN51efC2uYldmzvvnY')
        result_list = bing.search_all(query, limit=20, format='json')

        results = [result.url for result in result_list]
    except:
        return None
    return results[:min(5, len(results))]

parser, st, stop = common_lib.Init()

f = open("output_passages_big_bing.xml", "wb")
f.write("<data>\n")
e = xml.etree.ElementTree.parse('big_sample.xml').getroot()
i = 1
all_scores = 0
top_scores = 0
for ves in e.findall('vespaadd'):
    for doc in ves.findall('document'):
        if i < 20:
            i += 1
            continue
        f.write("<doc number = \"" + str(i) + "\">\n")
        try:
            # adding links for keyword query
            print "doc " + str(i)
            keyword_query = common_lib.buildFullQuery(doc.find('subject').text, doc.find('content').text, parser, stop)
            links_bing = GetLinksForQueryBing(keyword_query)
            f.write("<keyword_query>" + escape(keyword_query) + "</keyword_query>\n")
            keyword_query =  passage_retrieval.RemoveSynonymsFromKeywords(keyword_query)
            for link in links_bing:
                f.write("<link>\n")
                passages = passage_retrieval.GetScoredPassages(keyword_query, link)
                if not passages:
                    f.write("</link>\n")
                    continue
                for passage in passages:
                    f.write("<passage>\n")
                    f.write("<text>" + escape(passage[0].encode('utf-8')) + "</text>\n")
                    f.write("<score>" + str(passage[1]) + "</score>\n")
                    f.write("<top_answer_similarity>" + str(passage_retrieval.GetSimilarity(doc.find('bestanswer').text, passage[0])) + "</top_answer_similarity>\n")
                    f.write("</passage>\n")
                f.write("</link>\n")
        except:
            print "Error for doc " + str(i)
        f.write("</doc>\n")
        i += 1

f.write("</data>\n")
f.close()

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

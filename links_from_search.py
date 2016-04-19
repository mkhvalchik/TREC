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
def GetLinksForQuery(query):
    #service = build("customsearch", "v1",
    #          developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

    #res = service.cse().list(
    #    q=query,
    #    cx='000504779742960611072:dpmv5fihhu8',
    #  ).execute()

    #return [item['link'] for item in res['items']][:20]

    bing = PyBingSearch('3Bybyj2qcK/w5FXbBqBUjI9MajN51efC2uYldmzvvnY')
    result_list = bing.search_all(query, limit=20, format='json')

    return [result.url for result in result_list][:20]

# Returns a list of links appearing in search for a given request.
def GetLinksForQueries(queries):
    links = []
    for query in queries:
        links += GetLinksForQueries()
    # remove duplicates
    return list(set(links))

with open('output_links.txt') as data_file:
    links = json.load(data_file)

parser, st, stop = common_lib.Init()

f = open("output_links_small_bing.xml", "wb")
f.write("<data>\n")
e = xml.etree.ElementTree.parse('small_sample.xml').getroot()
i = 1
all_scores = 0
top_scores = 0
for ves in e.findall('vespaadd'):
    for doc in ves.findall('document'):
        f.write("<doc number = \"" + str(i) + "\">\n")

        # adding links for keyword query
        print "next doc"
        keyword_query = common_lib.buildFullQuery(doc.find('subject').text, doc.find('content').text, parser, stop)
        links_keywords = links[str(i - 1)][1]
        print links_keywords
        f.write("<keyword_query>" + escape(keyword_query) + "</keyword_query>\n")
        f.write("<links>\n")
        sum_score = 0
        len_score = 0
        j = 1
        max_score = 0
        passages = []
        scores = {}
        for link in links_keywords:
            f.write("<link_passage number = \"" + str(j) + "\">\n")
            f.write("<link>" + escape(link) + "</link>\n")
            passage, _ = passage_retrieval.GetTopPassageFromLink(keyword_query, link)
            if passage:
                passages.append(passage)
                score = passage_retrieval.GetSimilarity(doc.find('bestanswer').text, passage)
                scores[passage] = score
                sum_score += score
                if score > max_score:
                    max_score = score
                len_score += 1
                f.write("<best_passage_per_link>\n")
                f.write("<passage>" + escape(passage.encode('utf-8')) + "</passage>\n")
                f.write("<score>" + escape(str(score)) + "</score>\n")
                f.write("</best_passage_per_link>\n")
            f.write("</link_passage>\n")
            j += 1
        f.write("</links>\n")

        if len_score > 0:
            all_scores += float(sum_score) / len_score
            f.write("<avg_score>" + escape(str(float(sum_score) / len_score)) + "</avg_score>\n")
            f.write("<max_score>" + escape(str(max_score)) + "</max_score>\n")
            top_passage = passage_retrieval.GetTopPassageFromList(keyword_query, passages)
            f.write("<top_passage>" + escape(top_passage[0].encode('utf-8')) + "</top_passage>\n")
            top_scores += scores[top_passage[0]]
            f.write("<top_passage_score>" + str(float(scores[top_passage[0]])) + "</top_passage_score>\n")
        f.write("</doc>\n")
        i += 1

f.write("<avg_total_score>" + escape(str(float(all_scores) / (i - 1))) + "</avg_total_score>\n")
f.write("<avg_top_score>" + escape(str(float(top_scores) / (i - 1))) + "</avg_top_score>\n")
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
